import abc
import typing
import pydantic
import dataclasses

from ..Item import Item

from . import Action
from .Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Synthesizer(Processor, metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def process(self, input: Item, matched: typing.Iterable[Item]) -> typing.Iterable[Item.Status | Item]:
		pass

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, input: typing.Iterable[Item]) -> typing.Iterable[Action.Action]:

		iterator = input.__iter__()

		for i in iterator:
			for o in self.process(i, iterator):
				match o:
					case Item.Status():
						yield Action.Update(
							old = i,
							new = dataclasses.replace(i, status = o)
						)
					case Item():
						yield Action.Append(o)
			break