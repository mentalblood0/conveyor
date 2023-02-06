import abc
import typing
import datetime
import pydantic
import functools
import traceback

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
				lambda result, p: p(lambda: result, {}),
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


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Error(Action):

	old  : Item
	e    : Exception

	type : Item.Type

	@property
	def item(self) -> Item:
		return Item(
			type     = self.type,
			status   = Item.Status('created'),
			data     = Item.Data(value = '\n'.join(traceback.format_exception(self.e)).encode()),
			metadata = Item.Metadata({
				Item.Metadata.Key('error_type')  : Item.Metadata.Enumerable(self.e.__class__.__name__),
				Item.Metadata.Key('error_text')  : str(self.e),
				Item.Metadata.Key('item_type')   : Item.Metadata.Enumerable(self.old.type.value),
				Item.Metadata.Key('item_status') : Item.Metadata.Enumerable(self.old.status.value)
			}),
			chain    = Item.Chain(ref = Item.Data(value = b'')),
			reserver = Item.Reserver(exists = False, value = None),
			created  = Item.Created(datetime.datetime.now())
		)

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		Append(self.item)(repository)

	@property
	@pydantic.validate_arguments
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		yield ('old', self.old)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Solution(Action):

	old  : Item

	type : Item.Type

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		Delete(
			Error(
				old  = self.old,
				e    = Exception(),
				type = self.type
			).item
		)(repository)

	@property
	@pydantic.validate_arguments
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		yield ('old', self.old)