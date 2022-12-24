import typing
import pydantic

from .Item import Item
from .Part import Part
from .Query import Query



@pydantic.dataclasses.dataclass(frozen=True)
class PartRepository:

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		pass

	@pydantic.validate_arguments
	def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
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