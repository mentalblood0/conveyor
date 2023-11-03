import typing
import contextlib
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

    def _with_receiver(self, receiver: Receiver, config: typing.Any = None):
        iterator = iter(receiver(self.repository))
        with contextlib.suppress(RuntimeError):
            while True:
                self.actor(self.processor(iterator.__next__, config), self.repository)

    def _without_receiver(self, config: typing.Any = None):
        self.actor(self.processor(tuple, config), self.repository)

    def __call__(self, config: typing.Any = None):
        if self.receiver is None:
            self._without_receiver(config)
        else:
            self._with_receiver(self.receiver, config)
