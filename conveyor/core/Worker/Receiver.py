import typing
import pydantic

from ..Item import Item
from ..Query import Query
from ..Repository import Repository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Receiver:

	masks: typing.Sequence[
		typing.Callable[
			[typing.Sequence[Item]],
			Query.Mask
		]
	]

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> typing.Iterable[Item]:

		previous: typing.Sequence[Item] = []

		for f in self.masks:
			mask = f(previous)
			previous.clear()
			for item in repository[Query(mask = mask, limit = None)]:
				yield item
				previous.append(item)