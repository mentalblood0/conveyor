import os
import growing_tree_base
from peewee import Database
from functools import partial
from dataclasses import dataclass, replace

from ...common import Model
from ...core import Item, Repository

from . import Path, File, FileCache, ItemAdapter



@dataclass
class Treegres(Repository):

	db: Database
	dir_tree_root_path: str

	cache_size: int = 1024
	encoding: str = 'utf8'

	def __post_init__(self):

		if self.cache_size:
			self._getFile = FileCache(self.cache_size)
		else:
			self._getFile = File

		self._getFile = partial(self._getFile, encoding=self.encoding)
	
	def _getTypePath(self, type: str) -> str:
		return os.path.join(self.dir_tree_root_path, type.lower())

	def create(self, item):

		type_root = self._getTypePath(item.type)
		type_tree = growing_tree_base.Tree(
			root=type_root,
			base_file_name=''.join(
				f'.{e}'
				for e in File.extensions
			),
			save_file_function=lambda p, c: self._getFile(Path(p)).set(c)
		)
		file_path = type_tree.save(item.data)

		result_item = replace(
			item,
			data_digest=self._getFile(Path(file_path)).correct_digest
		)
		result_item.metadata['file_path'] = Path(os.path.relpath(file_path, type_root))

		return ItemAdapter(result_item, self.db).save()

	def reserve(self, type, status, id, limit=None):

		return ItemAdapter(
			db=self.db,
			item=Item(
				type=type,
				status=status,
				metadata={'file_path': ''}
			)
		).reserve(
			id=id,
			limit=limit
		)
	
	def unreserve(self, type, status, id):

		if not (model := Model(self.db, type)):
			return None

		return (
			model
			.update(reserved_by='')
			.where(
				model.reserved_by==id,
				model.status==status
			)
		).execute()

	def get(self, type, where=None, fields=None, limit=1, reserved_by=None):

		if not (model := Model(self.db, type)):
			return []
		
		where = where or {}

		if reserved_by:
			where['reserved_by'] = reserved_by

		ignored_fields = {'file_path', 'reserved_by'}

		if not fields:
			fields = set()
		else:
			fields = set(fields) - ignored_fields

		get_fields = {
			getattr(model, f)
			for f in fields
			if hasattr(model, f)
		}

		try:
			conditions = [
				getattr(model, key)==value
				for key, value in where.items()
			]
		except AttributeError:
			return []

		result = []

		query = model.select(*get_fields)
		if conditions:
			query = query.where(*conditions).limit(limit)

		for r in query:

			item = Item(
				type=type,
				**{
					name: getattr(r, name)
					for name in fields or r.__data__
					if name not in ignored_fields and hasattr(Item, name)
				},
				metadata={
					name: getattr(r, name)
					for name in fields or r.__data__
					if name not in ignored_fields and not hasattr(Item, name)
				}
			)

			if (fields and ('data' in fields)) or (not fields):
				item.data=self._getFile(
					Path(os.path.join(self._getTypePath(type), r.file_path))
				).get(r.data_digest)
		
			result.append(item)

		return result

	def update(self, item):
		return ItemAdapter(item, self.db).update()

	def delete(self, type, id):

		if not (model := Model(self.db, type)):
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

		if not (model := Model(self.db, type)):
			return None
		else:
			return self.db.drop_tables([model])
