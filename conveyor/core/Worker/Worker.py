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
		self.actor(
			self.processor(
				self.receiver(
					self.repository
				),
				config
			),
			self.repository
		)