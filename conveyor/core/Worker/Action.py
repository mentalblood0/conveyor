import abc
import typing
import pydantic

from ..Item import Item
from ..Repository.Repository import Repository

from .Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Action(metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def __call__(self, repository: Repository) -> None:
		pass

	@property
	@abc.abstractmethod
	def output(self) -> typing.Iterable[Item]:
		pass


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Actor:

	Processors = typing.Sequence[Processor[Action, Action]] | typing.Iterable[Processor[Action, Action]]

	processors : Processors = ()

	@pydantic.validate_arguments
	def _process(self, actions: typing.Iterable[Action], processors: Processors) -> typing.Iterable[Action]:
		for p in processors:
			return self._process(p(actions, {}), processors)
		return actions

	@pydantic.validate_arguments
	def __call__(self, actions: typing.Sequence[Action] | typing.Iterable[Action], repository: Repository) -> None:
		actions = (*actions,)
		with repository.transaction() as t:
			for a in self._process(actions, self.processors):
				a(t)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Append(Action):

	item : Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository.append(self.item)

	@property
	def output(self) -> typing.Iterable[Item]:
		yield self.item


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Update(Action):

	old : Item
	new : Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository[self.old] = self.new

	@property
	def output(self) -> typing.Iterable[Item]:
		yield self.new


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Delete(Action):

	item : Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		del repository[self.item]

	@property
	def output(self) -> typing.Iterable[Item]:
		raise StopIteration