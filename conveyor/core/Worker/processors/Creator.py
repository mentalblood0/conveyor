import abc
import typing
import pydantic

from ...Item import Item

from .. import Action
from ..Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Creator(Processor, metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def process(self, **kwargs: dict[str, typing.Any]) -> typing.Iterable[Item]:
		pass

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, _, **kwargs: dict[str, typing.Any]) -> typing.Iterable[Action.Action]:
		for o in self.process(**kwargs):
			yield Action.Append(o)