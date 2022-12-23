import typing
import pydantic

from .Item import Item
from .ItemPart import ItemPart
from .ItemQuery import ItemQuery



@pydantic.dataclasses.dataclass(frozen=True)
class PartRepository:

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
	def transaction(self, f: typing.Callable[[], None]) -> None:
		raise NotImplemented