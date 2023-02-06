import copy
import typing
import pydantic

from ..Item import Item
from ..Repository.Query import Query
from ..Repository.Repository import Repository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Receiver:

	MasksElement = typing.Callable[[typing.Sequence[Item]], Query.Mask]
	Masks        = typing.Sequence[MasksElement] | typing.Iterable[MasksElement]

	masks : Masks
	limit : Query.Limit

	@pydantic.validate_arguments
	def sequence(self, repository: Repository, first: Item, masks: Masks) -> typing.Iterable[Item]:

		yield first

		previous: typing.Sequence[Item] = [first]

		for f in masks:

			mask = f(previous)
			previous.clear()

			for item in repository[Query(mask = mask, limit = None)]:
				yield item
				previous.append(item)

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> typing.Iterable[typing.Iterable[Item]]:

		iterator = self.masks.__iter__()

		for f in iterator:
			for first in repository[Query(mask = f(()), limit = self.limit)]:
				yield self.sequence(repository, first, copy.deepcopy(iterator))
			break