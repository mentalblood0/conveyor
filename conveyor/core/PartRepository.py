import typing
import pydantic
import contextlib

from .Item import Item
from .Part import Part
from .Query import Query



@pydantic.dataclasses.dataclass(frozen=True)
class PartRepository:

	@pydantic.validate_arguments
	def append(self, item: Item) -> None:
		raise NotImplementedError

	@pydantic.validate_arguments
	def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
		raise NotImplementedError

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		raise NotImplementedError

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		raise NotImplementedError

	@pydantic.validate_arguments
	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:
		raise NotImplementedError

	@pydantic.validate_arguments
	def __contains__(self, item: Item) -> bool:
		raise NotImplementedError