import abc
import typing
import pydantic
import contextlib

from ..Item import Item
from ..Item.Part import Part
from .Query import Query



@pydantic.dataclasses.dataclass(frozen=True)
class PartRepository(metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def append(self, item: Item) -> None:
		pass

	@abc.abstractmethod
	def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
		pass

	def __setitem__(self, old: Item, new: Item) -> None:
		raise NotImplementedError

	@abc.abstractmethod
	def __delitem__(self, item: Item) -> None:
		pass

	@abc.abstractmethod
	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:
		pass

	@abc.abstractmethod
	def __contains__(self, item: Item) -> bool:
		pass

	@abc.abstractmethod
	def __len__(self) -> pydantic.NonNegativeInt:
		pass

	@abc.abstractmethod
	def clear(self) -> None:
		pass