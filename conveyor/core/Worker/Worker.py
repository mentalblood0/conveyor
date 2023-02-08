import typing
import pydantic

from .. import Item
from ..Repository.Repository import Repository

from .Receiver import Receiver
from .Processor import Processor
from .Action import Action, Actor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Worker:

	receiver   : Receiver
	processor  : Processor[Item, Action]
	actor      : Actor = Actor()

	repository : Repository

	def __call__(self, config: dict[str, typing.Any] = {}) -> None:

		iterator = iter(self.receiver(self.repository))
		received = False
		def _next():
			nonlocal received
			received = True
			return next(iterator)

		try:
			i = 0
			while True:
				if i == self.receiver.limit:
					break
				received = False
				self.actor(
					self.processor(
						_next,
						config
					),
					self.repository
				)
				if not received:
					break
				i += 1
		except RuntimeError:
			pass