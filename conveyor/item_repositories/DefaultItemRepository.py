import os
import lzma
import base64
from typing import Union
from blake3 import blake3
from growing_tree_base import *
from functools import lru_cache
from dataclasses import dataclass
from peewee import Database, Model as Model_
from peewee import CharField, FixedCharField, IntegerField, FloatField, DateTimeField

from .. import Item, ItemRepository, Model



def installLoggingCommon(db: Database, log_table_name: str='conveyor_log') -> None:

	log_model = Model(db, log_table_name, {
		'date': DateTimeField(),
		'chain_id': CharField(),
		'worker': CharField(null=True),
		'type': CharField(),
		'status_old': CharField(null=True),
		'status_new': CharField(null=True)
	})
	if not log_model.table_exists():
		db.create_tables([log_model])

	db.execute_sql('''
		CREATE OR REPLACE FUNCTION conveyor_log_function()
			RETURNS trigger as $$
			BEGIN
				INSERT INTO conveyor_log (
					date,
					chain_id,
					worker,
					type,
					status_old,
					status_new
				)
				VALUES (
					NOW()::timestamp,
					GREATEST(OLD.chain_id, NEW.chain_id),
					NEW.worker,
					TG_TABLE_NAME,
					OLD.status,
					NEW.status
				);
				RETURN NEW;
			END;
			$$ LANGUAGE 'plpgsql';
		'''
	)


def installLoggingForTable(db: Database, table_name: str) -> None:

	db.execute_sql(f'''
		CREATE OR REPLACE TRIGGER conveyor_log_trigger
			AFTER 
				INSERT OR 
				UPDATE OR 
				DELETE 
			ON {table_name}
			FOR EACH ROW
			EXECUTE PROCEDURE conveyor_log_function();
		'''
	)


class Path(str):
	def __new__(C, value):
		return super().__new__(
			C,
			os.path.normpath(os.path.normcase(value))
		)


def getFields(item: Item) -> dict[str, Union[str, int, float, Path]]:
	return {
		k: v
		for k, v in (item.metadata | item.__dict__).items()
		if not k in ['data', 'metadata', 'type', 'id']
	}


def getModel(db: Model_, item: Item) -> Model_:

	columns = {
		k: {
			str: CharField(default=''),
			int: IntegerField(default=0),
			float: FloatField(default=0.0),
			Path: FixedCharField(max_length=16)
		}[type(v)]
		for k, v in getFields(item).items()
	}

	model = Model(db, item.type, columns)
	if not model.table_exists():
		db.create_tables([model])
		installLoggingCommon(db)
		installLoggingForTable(db, model.__name__)

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
class DefaultItemRepository(ItemRepository):

	db: Database
	dir_tree_root_path: str
	cache_size: int=1024
	max_dirs_on_level: int=8
	max_files_on_level: int=8
	base_file_name: str='.xz'

	def __post_init__(self):
		self.getFileContent = lru_cache(maxsize=self.cache_size)(getFileContent)

	def create(self, item):

		item_data_bytes = item.data.encode('utf8')
		item.data_digest = getDigest(item_data_bytes)
		type_dir_path = os.path.join(self.dir_tree_root_path, item.type)

		file_absolute_path = saveToDirTree(
			file_content=item_data_bytes, 
			root_dir=type_dir_path,
			base_file_name=self.base_file_name,
			save_file_function=setFileContent,
			max_files_on_level=8,
			max_dirs_on_level=8
		)

		item.metadata['file_path'] = Path(os.path.relpath(file_absolute_path, type_dir_path))

		return getModel(self.db, item)(**getFields(item)).save()

	def get(self, type, status, limit=None):

		model = Model(self.db, type)
		if not model:
			return []

		query_result = model.select().where(model.status==status).limit(limit)
		result = []

		for r in query_result:

			file_path = Path(os.path.join(self.dir_tree_root_path, type, r.__data__['file_path']))

			item = Item(
				type=type,
				status=status,
				id=r.__data__['id'],
				chain_id=r.__data__['chain_id'],
				data_digest = r.__data__['data_digest'],
				data=self.getFileContent(file_path, r.__data__['data_digest'])
			)
			item.metadata = {
				k: v
				for k, v in r.__data__.items()
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
