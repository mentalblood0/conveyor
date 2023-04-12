import typing
from .. import Action as Action
from ... import Item as Item, Repository as Repository
from ..Processor import Processor as Processor

class Error(Action.Action):
    old: Item
    exception: Exception
    type: Item.Type
    @property
    def item(self) -> Item: ...
    def __call__(self, repository: Repository) -> None: ...
    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]: ...

class Solution(Action.Action):
    ref: Item | Action.Success
    type: Item.Type
    @property
    def old(self) -> Item: ...
    def __call__(self, repository: Repository) -> None: ...
    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]: ...

class Logger(Processor[Action.Action, Action.Action]):
    Error = Error
    Solution = Solution
    normal: Item.Type
    errors: Item.Type
    def __call__(self, input: typing.Callable[[], typing.Iterable[Action.Action]], config: dict[str, typing.Any]) -> typing.Iterable[Action.Action]: ...
