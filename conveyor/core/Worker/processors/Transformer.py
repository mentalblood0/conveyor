import abc
import typing
import pydantic
import dataclasses

from ...Item import Item

from .. import Action
from ..Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transformer(Processor[Item, Action.Action], metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def process(self, input: Item) -> typing.Iterable[Item.Status | Item.Metadata]:
		pass

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, input: typing.Callable[[], typing.Iterable[Item]], config: dict[str, typing.Any] = {}) -> typing.Iterable[Action.Action]:

		for i in input():

			try:
				for o in self.process(i):
					match o:
						case Item.Status():
							yield Action.Update(old = i, new = dataclasses.replace(i, status = o))
						case Item.Metadata():
							yield Action.Update(
								old = i,
								new = dataclasses.replace(
									i,
									metadata = Item.Metadata(value_ = i.metadata.value | o.value)
								)
							)
			except Exception as e:
				raise self.error(i, e)

			yield Action.Success(i)
			break