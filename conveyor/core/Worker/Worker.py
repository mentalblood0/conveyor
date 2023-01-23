import pydantic

from ..Repository import Repository

from . import Action
from .Receiver import Receiver
from .Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Worker:

	receiver:  Receiver
	processor: Processor

	repository: Repository

	def __call__(self):
		Action.Actor(
			self.processor(
				self.receiver(
					self.repository
				)
			)
		)(
			self.repository
		)