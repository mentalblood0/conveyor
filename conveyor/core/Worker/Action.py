import abc
import typing
import functools
import dataclasses

from ..Item import Item
from ..Repository.Repository import Repository

from .Processor import Processor


@dataclasses.dataclass(frozen=True, kw_only=False)
class Action(abc.ABC):
    @abc.abstractmethod
    def __call__(self, repository: Repository) -> None:
        """"""

    @property
    @abc.abstractmethod
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
        """"""


@dataclasses.dataclass(frozen=True, kw_only=False)
class Actor:
    Processors = (
        typing.Sequence[Processor[Action, Action]]
        | typing.Iterable[Processor[Action, Action]]
    )

    processors: Processors = ()

    def __call__(
        self,
        actions: typing.Sequence[Action] | typing.Iterable[Action],
        repository: Repository,
    ) -> None:
        actions = (*actions,)
        with repository.transaction() as t:
            for a in functools.reduce(
                lambda result, p: p(lambda: result, {}), self.processors, actions
            ):
                a(t)


@dataclasses.dataclass(frozen=True, kw_only=False)
class Append(Action):
    new: Item

    def __call__(self, repository: Repository) -> None:
        repository.append(self.new)

    @property
    def info(self):
        yield ("item", self.new)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Update(Action):
    old: Item
    new: Item

    def __call__(self, repository: Repository) -> None:
        repository[self.old] = self.new

    @property
    def info(self):
        yield ("old", self.old)
        yield ("new", self.new)


@dataclasses.dataclass(frozen=True, kw_only=False)
class Delete(Action):
    old: Item

    def __call__(self, repository: Repository) -> None:
        del repository[self.old]

    @property
    def info(self):
        yield ("item", self.old)


@dataclasses.dataclass(frozen=True, kw_only=False)
class Success(Action):
    item: Item

    def __call__(self, repository: Repository) -> None:
        return

    @property
    def info(self):
        yield ("item", self.item)
