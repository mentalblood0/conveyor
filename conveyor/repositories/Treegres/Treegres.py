import peewee
import typing
import pydantic
import dataclasses

from ...common import Model
from ...core import Item, Repository, Metadata

from . import Files, ItemAdapter



@dataclasses.dataclass(frozen=True)
class Treegres(Repository):

	db: peewee.Database
	files: Files

	@pydantic.validate_arguments
	def create(self, item: Item) -> None:
		self.files.append(item.data)
		ItemAdapter(item, self.db).save()

	@pydantic.validate_arguments
	def reserve(self, type: str, status: str, id: str, limit: int | None=None) -> None:

		model = Model(self.db, type)

		model.update(
			reserved_by=id
		).where(
			model.digest.in_(
				model
				.select(model.digest)
				.where(
					model.reserved==None,
					model.status==status
				)
				.order_by(peewee.fn.Random())
				.limit(limit)
			)
		).execute()

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		ItemAdapter(item, self.db).unreserve()

	@pydantic.validate_arguments
	def get(self, type: str, where: Metadata | None=None, limit: int | None=1, reserved: str | None=None) -> list[Item]:

		if not (model := Model(self.db, type)):
			return []

		where = where or {}
		if reserved:
			where['reserved'] = reserved

		query = model.select()
		if (conditions := [
			getattr(model, k)==v
			for k, v in where.items()
			if hasattr(model, k)
		]):
			query = query.where(*conditions)

		query = query.limit(limit)

		return [
			Item(
				type=type,
				data=self.files[r.digest],
				**{
					name: getattr(r, name)
					for name in r.__data__
					if name in Item.__dataclass_fields__
				},
				metadata={
					name: getattr(r, name)
					for name in r.__data__
					if name not in Item.__dataclass_fields__
				}
			)
			for r in query
		]

	@pydantic.validate_arguments
	def update(self, old: Item, new: Item) -> None:
		ItemAdapter(old, self.db).update(ItemAdapter(new, self.db))

	@pydantic.validate_arguments
	def delete(self, item: Item) -> None:
		ItemAdapter(item, self.db).delete()
		del self.files[item.data.digest]

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable[[typing.Callable], typing.Callable]:

		def new_f(*args, **kwargs):
			with self.db.transaction():
				result = f(*args, **kwargs)
			return result

		return new_f

	@pydantic.validate_arguments
	def _drop(self, type: str) -> None:
		self.db.drop_tables([
			Model(self.db, type)
		])
