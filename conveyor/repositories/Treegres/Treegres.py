import peewee
import typing
import pydantic
import dataclasses

from ...common import Model
from ...core import Item, Repository, Word, Chain

from . import Files, Rows



@dataclasses.dataclass(frozen=True)
class Treegres(Repository):

	db: peewee.Database
	files: Files

	@pydantic.validate_arguments
	def create(self, item: Item) -> None:
		self.files.add(item.data)
		ItemAdapter(item=item, db=self.db).save()

	@pydantic.validate_arguments
	def reserve(self, type: str, status: str, id: str, limit: int | None=None) -> None:

		model = Model(self.db, Word(type))

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
		ItemAdapter(item=item, db=self.db).unreserve()

	@pydantic.validate_arguments
	def get(self, type: Word, where: dict[Word, Item.Value] | None=None, limit: int | None=1, reserved: str | None=None) -> list[Item]:

		if not (model := Model(self.db, type)):
			return []

		where = where or {}
		if reserved:
			where[Word('reserved')] = reserved

		query = model.select()
		if (conditions := [
			getattr(model, k.value)==v
			for k, v in where.items()
			if hasattr(model, k.value)
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
				metadata=Item.Metadata({
					Word(name): getattr(r, name)
					for name in r.__data__
					if name not in Item.__dataclass_fields__
				})
			)
			for r in query
		]

	@pydantic.validate_arguments
	def update(self, old: Item, new: Item) -> None:
		ItemAdapter(item=old, db=self.db).update(ItemAdapter(item=new, db=self.db))

	@pydantic.validate_arguments
	def delete(self, item: Item) -> None:
		ItemAdapter(item=item, db=self.db).delete()
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
			Model(self.db, Word(type))
		])
