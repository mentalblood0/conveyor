import os
import growing_tree_base
from peewee import Database
from functools import lru_cache
from dataclasses import dataclass, asdict, replace

from ...common import Model
from ...core import Item, Repository

from . import Path, File, getDigest, ItemAdapter



@dataclass
class Treegres(Repository):

	db: Database
	dir_tree_root_path: str

	cache_size: int = 1024

	def __post_init__(self):
		if self.cache_size:
			self.File = lru_cache(maxsize=self.cache_size)(File)
		else:
			self.File = File

	def create(self, item):

		item_data_bytes = item.data.encode('utf8')
		item.data_digest = getDigest(item_data_bytes)
		type_dir_path = os.path.join(self.dir_tree_root_path, item.type)

		file_absolute_path = growing_tree_base.Tree(
			root=type_dir_path,
			base_file_name='.xz',
			save_file_function=lambda p, c: self.File(Path(p)).set(c)
		).save(item_data_bytes)

		result_item = replace(
			item,
			data_digest=getDigest(item_data_bytes),
			metadata=(
				item.metadata
				| {'file_path': Path(os.path.relpath(file_absolute_path, type_dir_path))}
			)
		)

		return ItemAdapter(result_item, self.db).save()

	def fetch(self, type, status, limit=None):

		model = Model(self.db, type)
		if not model:
			return []

		query_result = model.select().where(model.status==status).limit(limit)
		result = []

		for r in query_result:

			r_dict = {
				k: v
				for k, v in r.__data__.items()
			}

			file_path = Path(os.path.join(self.dir_tree_root_path, type, r_dict['file_path']))

			item = Item(
				type=type,
				status=status,
				id=r_dict['id'],
				chain_id=r_dict['chain_id'],
				data_digest = r_dict['data_digest'],
				data=self.File(file_path).get(r_dict['data_digest'])
			)
			item.metadata = {
				k: v
				for k, v in r_dict.items()
				if k not in asdict(item)
			}

			result.append(item)

		return result
	
	def get(self, type, where=None, fields=None, limit=1):

		model = Model(self.db, type)
		if not model:
			return []

		if fields == None:
			get_fields = []
		else:
			get_fields = [
				getattr(model, f)
				for f in fields
				if hasattr(model, f)
			]

		conditions = [
			getattr(model, key)==value
			for key, value in where.items()
		]
		query_result = model.select(*get_fields).where(*conditions).limit(limit)

		result = []

		for r in query_result:

			if fields == None:

				file_path = Path(os.path.join(self.dir_tree_root_path, type, r.file_path))

				item = Item(
					type=type,
					status=r.status,
					id=r.id,
					chain_id=r.chain_id,
					data_digest = r.data_digest,
					data=self.File(file_path).get(r.data_digest)
				)
				item.metadata = {
					k: v
					for k, v in r.__data__.items()
					if k not in asdict(item)
				}

			else:

				item = Item(type=type, **{
					name: getattr(r, name)
					for name in fields
					if hasattr(r, name)
				})

				if 'data' in fields:
					file_path = Path(os.path.join(self.dir_tree_root_path, type, r.file_path))
					item.data=self.File(file_path).get(r.data_digest)
				
				if 'metadata' in fields:
					item.metadata = {
						k: v
						for k, v in r.__data__.items()
						if k not in asdict(item)
					}
		
			result.append(item)

		return result

	def update(self, item):
		return ItemAdapter(item, self.db).update()

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
