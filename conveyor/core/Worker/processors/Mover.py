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

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def error(self, i: Item, exception: Exception) -> typing.Iterable[Action.Action]:
		yield Action.Error(
			old       = i,
			exception = exception,
			type      = Item.Type('conveyor_errors')
		)

	@pydantic.validate_arguments
	def _handle(self, i: Item, other: typing.Iterable[Item], config: dict[str, typing.Any]) -> typing.Iterable[Action.Action]:
		for o in self.process(i):
			match o:
				case Item.Status():
					yield Action.Update(old = i, new = dataclasses.replace(i, status = o))
				case Item():
					if o.chain != i.chain:
						raise ValueError(f'Output chain ({o.chain}) must be equal to input chain ({i.chain})')
					yield Action.Append(o)

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, input: typing.Callable[[], typing.Iterable[Item]], config: dict[str, typing.Any] = {}) -> typing.Iterable[Action.Action]:
		for i in input():
			for a in self._handle(i, (), config):
				yield a
			break