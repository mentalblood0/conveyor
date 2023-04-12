import abc
import typing
from ..Item import Item as Item
from ..Repository.Repository import Repository as Repository
from .Processor import Processor as Processor
from _typeshed import Incomplete

class Action(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, repository: Repository) -> None: ...
    @property
    @abc.abstractmethod
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]: ...

class Actor:
    Processors: Incomplete
    processors: Processors
    def __call__(self, actions: typing.Sequence[Action] | typing.Iterable[Action], repository: Repository) -> None: ...

class Append(Action):
    new: Item
    def __call__(self, repository: Repository) -> None: ...
    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]: ...

class Update(Action):
    old: Item
    new: Item
    def __call__(self, repository: Repository) -> None: ...
    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]: ...

class Delete(Action):
    old: Item
    def __call__(self, repository: Repository) -> None: ...
    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]: ...

class Success(Action):
    item: Item
    def __call__(self, repository: Repository) -> None: ...
    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]: ...
