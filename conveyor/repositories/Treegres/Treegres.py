import os
import pydantic
import dataclasses
import growing_tree_base
from peewee import Database
from functools import partial
from typing import Any, Iterable

from ...common import Model, ItemId
from ...core import Item, Repository
from ...common.ModelsCache import models_cache

from . import Path, File, FileCache, ItemAdapter



@dataclasses.dataclass(frozen=True)
class Treegres(Repository):

	db: Database
	dir_tree_root_path: str

	cache_size: int = 1024
	encoding: str = 'utf8'
	file_extensions: Iterable[str] = dataclasses.field(default_factory=partial(list, ['xml', 'xz']))

	def __post_init__(self):
		object.__setattr__(
			self,
			'_getFile',
			partial(
				(
					FileCache(self.cache_size)
					if self.cache_size
					else File
				),
				encoding=self.encoding
			)
		)

	@pydantic.validate_arguments
	def create(self, item: Item, ref: Item = None) -> int:

		result_item = None

		if not (ref is None):

			if (ref.data_digest == item.data_digest):

				result_item = dataclasses.replace(item)
				result_item.metadata['file_path'] = ref.metadata['file_path']

		if result_item is None:

			type_tree = growing_tree_base.Tree(
				root=os.path.join(self.dir_tree_root_path, item.type.lower()),
				base_file_name=''.join(
					f'.{e}'
					for e in self.file_extensions
				),
				save_file_function=lambda p, c: self._getFile(Path(p)).set(c)
			)
			file_path = type_tree.save(item.data)

			result_item = dataclasses.replace(
				item,
				data_digest=self._getFile(Path(file_path)).correct_digest
			)
			result_item.metadata['file_path'] = Path(os.path.relpath(file_path, self.dir_tree_root_path))

		return ItemAdapter(result_item, self.db).save()

	@pydantic.validate_arguments
	def reserve(self, type: str, status: str, id: str, limit: int | None=None) -> int:

		if not (model := Model(self.db, type)):
			return None

		return (
			model
			.update(reserved_by=id)
			.where(
				model.id.in_(
					model
					.select(model.id)
					.where(
						model.reserved_by==None,
						model.status==status
					)
					.limit(limit)
				)
			)
		).execute()

	@pydantic.validate_arguments
	def unreserve(self, type: str, ids: list[ItemId]) -> int:

		if not (model := Model(self.db, type)):
			return None

		return (
			model
			.update(reserved_by=None)
			.where(model.id << ids)
		).execute()

	@pydantic.validate_arguments
	def get(self, type: str, where: dict[str, Any]=None, fields: list[str]=None, limit: int | None=1, reserved_by: str=None) -> list[Item]:

		if not (model := Model(self.db, type)):
			return []

		where = where or {}
		if reserved_by:
			where['reserved_by'] = reserved_by

		ignored_fields = {'reserved_by'}
		fields = set(fields or []) - ignored_fields

		query = model.select(*{
			getattr(model, f)
			for f in fields
			if hasattr(model, f)
		})
		if (conditions := [
			getattr(model, key)==value
			for key, value in where.items()
			if hasattr(model, key)
		]):
			query = query.where(*conditions)

		query = query.limit(limit)

		return [
			Item(
				type=type,
				data=(
					self._getFile(
						Path(os.path.join(self.dir_tree_root_path, r.file_path))
					).get(r.data_digest)
					if (fields and ('data' in fields)) or (not fields)
					else ''
				),
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
			for r in query
		]

	@pydantic.validate_arguments
	def update(self, item: Item) -> int:
		return ItemAdapter(item, self.db).update()

	@pydantic.validate_arguments
	def delete(self, type: str, id: str) -> int:

		if not (model := Model(self.db, type)):
			return None

		relative_path = model.select().where(model.id==id).get().file_path
		full_path = Path(os.path.join(self.dir_tree_root_path, type, relative_path))

		result = model.delete().where(model.id==id).execute()

		try:
			os.remove(full_path)
		except FileNotFoundError:
			pass

		if isinstance(self._getFile, FileCache):
			self._getFile.delete(full_path)
		
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
