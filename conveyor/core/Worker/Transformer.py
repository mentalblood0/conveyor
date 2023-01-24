import abc
import typing
import pydantic
import dataclasses

from ..Item import Item

from . import Action
from .Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transformer(Processor, metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def process(self, input: Item) -> tuple[Item.Status, Item.Metadata]:
		pass

	@pydantic.validate_arguments
	def __call__(self, input: typing.Iterable[Item]) -> typing.Iterable[Action.Action]:

		i                = input.__iter__().__next__()
		status, metadata = self.process(i)

		yield Action.Update(
			old = i,
			new = dataclasses.replace(
				i,
				status   = status,
				metadata = metadata
			)
		)