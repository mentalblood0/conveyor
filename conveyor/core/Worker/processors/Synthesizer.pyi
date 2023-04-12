import abc
import typing
from .. import Action as Action
from ...Item import Item as Item
from ..Processor import Processor as Processor

class Synthesizer(Processor[Item, Action.Action], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def process(self, input: Item, matched: typing.Iterable[Item]) -> typing.Iterable[Item.Status | Item]: ...
    def __call__(self, input: typing.Callable[[], typing.Iterable[Item]], config: dict[str, typing.Any] = ...) -> typing.Iterable[Action.Action]: ...
