import os
import lzma
import base64
import growing_tree_base
from typing import Union
from blake3 import blake3
from functools import lru_cache
from dataclasses import dataclass
from peewee import Database, Model as Model_
from peewee import CharField, CharField, IntegerField, FloatField

from .. import Item, Repository, Model



class Path(str):
	def __new__(C, value):
		return super().__new__(
			C,
			os.path.normpath(os.path.normcase(value))
		)


def getFields(item: Item) -> dict[str, Union[str, int, float, Path]]:
	return {
		k: v or (None if type(v) == str else v)
		for k, v in (item.metadata | item.__dict__).items()
		if not k in ['data', 'metadata', 'type', 'id']
	}


def getModel(db: Model_, item: Item, path_length: int) -> Model_:

	columns = {
		k: {
			'chain_id': CharField(max_length=63),
			'status': CharField(max_length=63),
			'data_digest': CharField(max_length=63)
		}[k]
		for k in item.__dict__
		if not k in ['data', 'metadata', 'type', 'id']
	}

	columns |= {
		k: {
			str: CharField(default=None, null=True),
			int: IntegerField(default=None, null=True),
			float: FloatField(default=None, null=True),
			Path: CharField(max_length=path_length)
		}[type(v)]
		for k, v in item.metadata.items()
	}

	model = Model(db, item.type, columns)

	return model


def getDigest(data: bytes) -> str:
	d = blake3(data, max_threads=blake3.AUTO).digest()
	return base64.b64encode(d).decode('ascii')


def setFileContent(path: str, content: bytes) -> None:

	with lzma.open(path, 'wb', filters=[
		{"id": lzma.FILTER_LZMA2, "preset": lzma.PRESET_EXTREME},
	]) as f:
		f.write(content)


def getFileContent(path: str, digest: str) -> str:

	with lzma.open(path, 'rb') as f:
		file_content = f.read()
	
	correct_digest = getDigest(file_content)
	if correct_digest != digest:
		raise Exception(f"Cannot get file content: digest invalid: '{digest}' != '{correct_digest}'")

	return file_content.decode()


@dataclass
class Treegres(Repository):

	db: Database
	dir_tree_root_path: str
	cache_size: int=1024
	base_file_name: str='.xz'
	max_files_number: int=10**10

	def __post_init__(self):
		self.getFileContent = lru_cache(maxsize=self.cache_size)(getFileContent)
		self.path_length = growing_tree_base.calc.getPathLengthForFilesNumber(
			self.max_files_number,
			len(self.base_file_name)
		)

	def create(self, item):

		item_data_bytes = item.data.encode('utf8')
		item.data_digest = getDigest(item_data_bytes)
		type_dir_path = os.path.join(self.dir_tree_root_path, item.type)

		file_absolute_path = growing_tree_base.saveToDirTree(
			file_content=item_data_bytes,
			root_dir=type_dir_path,
			base_file_name=self.base_file_name,
			save_file_function=setFileContent,
			max_files_on_level=8,
			max_dirs_on_level=8
		)

		item.metadata['file_path'] = Path(os.path.relpath(file_absolute_path, type_dir_path))

		return getModel(self.db, item, self.path_length)(**getFields(item)).save()

	def get(self, type, status, limit=None):

		model = Model(self.db, type)
		if not model:
			return []

		query_result = model.select().where(model.status==status).limit(limit)
		result = []

		for r in query_result:

			r_dict = {
				k: v if v.__class__ == str else v
				for k, v in r.__data__.items()
			}

			file_path = Path(os.path.join(self.dir_tree_root_path, type, r_dict['file_path']))

			item = Item(
				type=type,
				status=status,
				id=r_dict['id'],
				chain_id=r_dict['chain_id'],
				data_digest = r_dict['data_digest'],
				data=self.getFileContent(file_path, r_dict['data_digest'])
			)
			item.metadata = {
				k: v
				for k, v in r_dict.items()
				if not k in [*item.__dict__.keys()]
			}

			result.append(item)
		
		return result
	
	def update(self, type, id, item):

		model = Model(self.db, type)
		if not model:
			return None

		return model.update(**getFields(item)).where(model.id==id).execute()

	def delete(self, type, id):

		model = Model(self.db, type)
		if not model:
			return None

		file_path = Path(model.select().where(model.id==id).get().__data__['file_path'])

		result = model.delete().where(model.id==id).execute()

		try:
			os.remove(file_path)
		except FileNotFoundError:
			pass
		
		return result

	@property
	def transaction(self):

		def decorator(f):
			def new_f(*args, **kwargs):
				with self.db.transaction():
					result = f(*args, **kwargs)
				return result
			return new_f

		return decorator
	
	def _drop(self, type: str) -> int:

		model = Model(self.db, type)
		if not model:
			return None
		
		return self.db.drop_tables([model])
