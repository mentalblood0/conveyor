import abc
import typing
import pydantic
import dataclasses

from ..Item import Item
from ..Query import Query
from ..Repository import Repository

from . import Action
from .Worker import Worker
from .Receiver import Receiver
from .Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Mover:

	input_type:   Item.Type
	input_status: Item.Status

	@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
	class Processor(Processor, metaclass = abc.ABCMeta):

		process: typing.Callable[[Item], tuple[Item.Status, Item]]

		@pydantic.validate_arguments
		def __call__(self, input: typing.Iterable[Item]) -> typing.Iterable[Action.Action]:

			i         = input.__iter__().__next__()
			status, o = self.process(i)

			yield Action.Update(
				old = i,
				new = dataclasses.replace(i, status = status)
			)
			yield Action.Append(o)

	@property
	@typing.final
	def receiver(self) -> Receiver:
		return Receiver((
			lambda _: Query.Mask(
				type   = self.input_type,
				status = self.input_status
			),
		))

	@abc.abstractmethod
	def process(self, item: Item) -> tuple[Item.Status, Item]:
		pass

	@property
	@typing.final
	def processor(self) -> Processor:
		return Mover.Processor(self.process)

	@pydantic.validate_arguments
	@typing.final
	def worker(self, repository: Repository) -> Worker:
		return Worker(
			receiver   = self.receiver,
			processor  = self.processor,
			repository = repository
		)