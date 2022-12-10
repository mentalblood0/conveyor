import typing
import pydantic

from . import Item, ItemQuery, ItemPart



@pydantic.dataclasses.dataclass(frozen=True)
class PartRepository:

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserver) -> None:
		pass

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		pass

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		pass

	@pydantic.validate_arguments
	def get(self, item_query: ItemQuery, accumulator: ItemPart) -> typing.Iterable[ItemPart]:
		raise NotImplemented

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		pass

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		pass

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:
		raise NotImplemented