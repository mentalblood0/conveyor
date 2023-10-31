import typing
import dataclasses

from .. import Item
from ..Repository.Repository import Repository

from .Receiver import Receiver
from .Processor import Processor
from .Action import Action, Actor


@dataclasses.dataclass(frozen=True, kw_only=True)
class Worker:
    receiver: Receiver | None = None
    processor: Processor[Item, Action]
    actor: Actor = Actor()

    repository: Repository

    def __call__(self, config: typing.Any = {}) -> None:
        match self.receiver:
            case Receiver():
                iterator = iter(self.receiver(self.repository))
                received = True

                def _next():
                    nonlocal received
                    received = True
                    return next(iterator)

                try:
                    while received:
                        received = False
                        self.actor(self.processor(_next, config), self.repository)
                except RuntimeError:
                    pass

            case None:
                self.actor(self.processor(lambda: (), config), self.repository)
