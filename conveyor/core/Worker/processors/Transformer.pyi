import abc
import typing
from .. import Action as Action
from ...Item import Item as Item
from ..Processor import Processor as Processor

class Transformer(Processor[Item, Action.Action], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def process(self, input: Item) -> typing.Iterable[Item.Status | Item.Metadata]: ...
    def __call__(self, input: typing.Callable[[], typing.Iterable[Item]], config: dict[str, typing.Any] = ...) -> typing.Iterable[Action.Action]: ...
