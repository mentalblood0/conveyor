import abc
import typing
import pydantic
import functools

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
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		pass


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Actor:

	Processors = typing.Sequence[Processor[Action, Action]] | typing.Iterable[Processor[Action, Action]]

	processors : Processors = ()

	@pydantic.validate_arguments
	def __call__(self, actions: typing.Sequence[Action] | typing.Iterable[Action], repository: Repository) -> None:
		actions = (*actions,)
		with repository.transaction() as t:
			for a in functools.reduce(
				lambda result, p: p(result, {}),
				self.processors,
				actions
			):
				a(t)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Append(Action):

	new : Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository.append(self.new)

	@property
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		yield ('item', self.new)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Update(Action):

	old : Item
	new : Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository[self.old] = self.new

	@property
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		yield ('old', self.old)
		yield ('new', self.new)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Delete(Action):

	old : Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		del repository[self.old]

	@property
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		yield ('item', self.old)