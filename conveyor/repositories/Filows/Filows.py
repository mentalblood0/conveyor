import typing
import pydantic
import dataclasses

from ...core import Item, ItemQuery

from . import Files, Rows, RowsItem



@dataclasses.dataclass(frozen=True, kw_only=True)
class Filows:

	rows: Rows
	files: Files

	@pydantic.validate_arguments
	def create(self, item: Item) -> None:
		self.files.add(item.data)
		self.rows.add(RowsItem(item))

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserved) -> None:
		self.rows.reserve(item_query, reserver)

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		self.rows.unreserve(RowsItem(item))

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		self.rows[RowsItem(old)] = RowsItem(new)

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Item]:
		for r in self.rows[item_query]:
			yield r.item(self.files[r.digest])

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		del self.rows[RowsItem(item)]
		del self.files[item.data.digest]

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable[[typing.Callable], typing.Callable]:
		return self.rows.transaction(f)