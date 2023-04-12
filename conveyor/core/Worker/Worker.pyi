import typing
from .. import Item as Item
from ..Repository.Repository import Repository as Repository
from .Action import Action as Action, Actor as Actor
from .Processor import Processor as Processor
from .Receiver import Receiver as Receiver

class Worker:
    receiver: Receiver | None
    processor: Processor[Item, Action]
    actor: Actor
    repository: Repository
    def __call__(self, config: dict[str, typing.Any] = ...) -> None: ...
