import abc
import typing
import pydantic

from ..Item import Item

from .Action import Action



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Processor(metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def __call__(self, input: typing.Iterable[Item], config: dict[str, typing.Any]) -> typing.Iterable[Action]:
		pass
