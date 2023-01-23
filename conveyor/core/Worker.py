import abc
import typing
import pydantic

from .Item import Item
from .Query import Query
from .Repository import Repository



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
			for item in repository[Query(mask = mask, limit = 128)]:
				yield item
				previous.append(item)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Action(metaclass = abc.ABCMeta):
	@abc.abstractmethod
	def __call__(self, repository: Repository) -> None:
		pass


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Append(Action):

	item: Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository.append(self.item)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Update:

	old: Item
	new: Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository[self.old] = self.new



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Delete:

	item: Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		del repository[self.item]


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Processor(metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def __call__(self, input: typing.Iterable[Item]) -> typing.Iterable[Action]:
		pass


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Actor:

	actions: typing.Iterable[Action]

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		for a in self.actions:
			a(repository)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Worker:

	receiver:  Receiver
	processor: Processor

	repository: Repository

	def __call__(self):
		Actor(
			self.processor(
				self.receiver(
					self.repository
				)
			)
		)(
			self.repository
		)