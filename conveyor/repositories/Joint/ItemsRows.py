import typing
import pydantic

from . import Rows, Row
from ...core import Item, ItemQuery



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class ItemsRows:

	rows: Rows

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserved) -> None:
		return self.rows.reserve(item_query, reserver)

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		return self.rows.unreserve(self.rows.Item.from_item(item))

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		return self.rows.add(self.rows.Item.from_item(item))

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Row]:
		return self.rows[item_query]

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		return self.rows.__setitem__(self.rows.Item.from_item(old), self.rows.Item.from_item(new))

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		return self.rows.__delitem__(self.rows.Item.from_item(item))

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:
		return self.rows.transaction(f)