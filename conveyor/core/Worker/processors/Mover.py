import abc
import typing
import pydantic
import dataclasses

from ...Item import Item

from .. import Action
from ..Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Mover(Processor[Item, Action.Action], metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def process(self, input: Item) -> typing.Iterable[Item.Status | Item]:
		pass

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, input: typing.Callable[[], typing.Iterable[Item]], config: dict[str, typing.Any] = {}) -> typing.Iterable[Action.Action]:
		for i in input():
			for o in self.process(i):
				match o:
					case Item.Status():
						yield Action.Update(old = i, new = dataclasses.replace(i, status = o))
					case Item():
						if o.chain != i.chain:
							raise ValueError(f'Output chain ({o.chain}) must be equal to input chain ({i.chain})')
						yield Action.Append(o)
			break