import typing
import pydantic

from ..Repository.Repository import Repository

from .Action import Actor
from .Receiver import Receiver
from .Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Worker:

	receiver:   Receiver
	processor:  Processor

	repository: Repository

	def __call__(self, config: dict[str, typing.Any] = {}) -> None:
		Actor(
			self.processor(
				self.receiver(
					self.repository
				),
				config
			)
		)(
			self.repository
		)