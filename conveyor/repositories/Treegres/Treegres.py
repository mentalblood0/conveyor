import os
import growing_tree_base
from peewee import Database
from dataclasses import dataclass, replace

from ...common import Model
from ...core import Item, Repository

from . import Path, File, FileCache, ItemAdapter



@dataclass
class Treegres(Repository):

	db: Database
	dir_tree_root_path: str

	cache_size: int = 1024

	def __post_init__(self):
		if self.cache_size:
			self._getFile = FileCache(self.cache_size)
		else:
			self._getFile = File
	
	def _getTypePath(self, type: str) -> str:
		return os.path.join(self.dir_tree_root_path, type.lower())

	def create(self, item):

		type_root = self._getTypePath(item.type)
		type_tree = growing_tree_base.Tree(
			root=type_root,
			base_file_name=f'.{File.extension}',
			save_file_function=lambda p, c: self._getFile(Path(p)).set(c)
		)
		file_path = type_tree.save(item.data.encode('utf8'))

		result_item = replace(
			item,
			data_digest=self._getFile(Path(file_path)).correct_digest
		)
		result_item.metadata['file_path'] = Path(os.path.relpath(file_path, type_root))

		return ItemAdapter(result_item, self.db).save()
	
	def get(self, type, where=None, fields=None, limit=1):

		model = Model(self.db, type)
		if not model:
			return []

		if not fields:
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

		result = []

		for r in model.select(*get_fields).where(*conditions).limit(limit):

			item = Item(type=type)

			for name in fields or r.__data__:

				value = getattr(r, name)

				if hasattr(item, name):
					setattr(item, name, value)
				else:
					item.metadata[name] = value

			if (fields and ('data' in fields)) or (not fields):
				item.data=self._getFile(
					Path(os.path.join(self._getTypePath(type), r.file_path))
				).get(r.data_digest)
		
			result.append(item)

		return result

	def update(self, item):
		return ItemAdapter(item, self.db).update()

	def delete(self, type, id):

		model = Model(self.db, type)
		if not model:
			return None

		relative_path = model.select().where(model.id==id).get().file_path
		full_path = os.path.join(self.dir_tree_root_path, type, relative_path)

		result = model.delete().where(model.id==id).execute()

		try:
			os.remove(full_path)
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
