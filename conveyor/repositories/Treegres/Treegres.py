import peewee
import typing
import pydantic
import dataclasses

from ...common import Model
from ...core import Item, Repository, Word

from . import Files, Rows, RowsItem



@dataclasses.dataclass(frozen=True)
class Treegres(Repository):

	rows: Rows
	files: Files

	@pydantic.validate_arguments
	def create(self, item: Item) -> None:
		self.files.add(item.data)
		self.rows.save(RowsItem(item))

	@pydantic.validate_arguments
	def reserve(self, type: str, status: str, id: str, limit: int | None=None) -> None:

		model = Model(self.rows.db, Word(type))

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
		self.rows.unreserve(RowsItem(item))

	@pydantic.validate_arguments
	def get(self, type: Word, where: dict[Word, Item.Value] | None=None, limit: int | None=1, reserved: str | None=None) -> list[Item]:

		if not (model := Model(self.rows.db, type)):
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
		self.rows.update(
			old=RowsItem(old),
			new=RowsItem(new)
		)

	@pydantic.validate_arguments
	def delete(self, item: Item) -> None:
		self.rows.delete(RowsItem(item))
		del self.files[item.data.digest]

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable[[typing.Callable], typing.Callable]:

		def new_f(*args, **kwargs):
			with self.rows.db.transaction():
				result = f(*args, **kwargs)
			return result

		return new_f
