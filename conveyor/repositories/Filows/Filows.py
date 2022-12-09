import typing
import pydantic
import dataclasses

from ...core import Item, ItemQuery

from . import ItemsFiles, ItemsRows



@dataclasses.dataclass(frozen=True, kw_only=True)
class Filows:

	rows: ItemsRows
	files: ItemsFiles

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		self.files.add(item)
		self.rows.add(item)

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserved) -> None:
		self.rows.reserve(item_query, reserver)

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		self.rows.unreserve(item)

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		self.rows[old] = new

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Item]:
		for r in self.rows[item_query]:
			yield r.item(self.files[r.digest])

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		del self.rows[item]
		del self.files[item]

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:
		return self.rows.transaction(
			self.files.transaction(f)
		)