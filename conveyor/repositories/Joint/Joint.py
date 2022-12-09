import typing
import pydantic
import dataclasses

from ...core import Item, ItemQuery

from . import ItemsFiles, ItemsRows



@dataclasses.dataclass(frozen=True, kw_only=True)
class Joint:

	parts: list[ItemsRows | ItemsFiles]

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserved) -> None:
		for p in reversed(self.parts):
			p.reserve(item_query, reserver)

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		for p in reversed(self.parts):
			p.unreserve(item)

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		for p in reversed(self.parts):
			p.add(item)

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Item]:
		for r in self.rows[item_query]:
			yield r.item(self.files[r.digest])

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		for p in reversed(self.parts):
			p[old] = new

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		for p in self.parts:
			del p[item]

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:

		result = self.parts[-1].transaction(f)
		for p in reversed(self.parts[:-1]):
			result = p.transaction(result)

		return result