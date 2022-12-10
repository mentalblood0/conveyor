import typing
import pydantic
import dataclasses

from ._Rows import _Rows
from ...core import Item, ItemQuery, ItemPart, PartRepository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Rows(PartRepository):

	rows: _Rows

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
	def get(self, item_query: ItemQuery, accumulator: ItemPart) -> typing.Iterable[ItemPart]:
		for r in self.rows[item_query]:
			yield dataclasses.replace(
				accumulator,
				type_=r.type,
				status_=r.status,
				digest_=r.digest,
				metadata_=r.metadata,
				created_=r.created,
				reserved_=r.reserved,
				reserver_=r.reserver
			)

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		return self.rows.__setitem__(self.rows.Item.from_item(old), self.rows.Item.from_item(new))

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		return self.rows.__delitem__(self.rows.Item.from_item(item))

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:
		return self.rows.transaction(f)