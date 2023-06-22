import abc
import typing
import pydantic

from ...Item import Item

from .. import Action
from ..Processor import Processor



@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Creator(Processor[Item, Action.Action], metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def process(self, config: dict[str, typing.Any]) -> typing.Iterable[Item]:
		pass

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, input: typing.Callable[[], typing.Iterable[Item]], config: dict[str, typing.Any]) -> typing.Iterable[Action.Action]:
		for o in self.process(config):
			yield Action.Append(o)