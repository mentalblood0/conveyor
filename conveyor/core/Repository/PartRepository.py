import abc
import typing
import contextlib
import dataclasses

from ..Item import Item
from ..Item.Part import Part
from .Query import Query


@dataclasses.dataclass(frozen=True)
class PartRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def append(self, item: Item) -> None:
        """"""

    @abc.abstractmethod
    def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
        """"""

    def __setitem__(self, old: Item, new: Item) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def __delitem__(self, item: Item) -> None:
        """"""

    @abc.abstractmethod
    @contextlib.contextmanager
    def transaction(self) -> typing.Iterator[typing.Self]:
        """"""

    @abc.abstractmethod
    def __contains__(self, item: Item) -> bool:
        """"""

    @abc.abstractmethod
    def __len__(self) -> int:
        """"""

    @abc.abstractmethod
    def clear(self) -> None:
        """"""
