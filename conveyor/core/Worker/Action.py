import abc
import typing
import pydantic

from ..Item import Item
from ..Repository import Repository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Action(metaclass = abc.ABCMeta):
	@abc.abstractmethod
	def __call__(self, repository: Repository) -> None:
		pass


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Actor:

	actions: typing.Iterable[Action]

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		with repository.transaction() as t:
			for a in self.actions:
				a(t)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Append(Action):

	item: Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository.append(self.item)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Update(Action):

	old: Item
	new: Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		repository[self.old] = self.new


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Delete(Action):

	item: Item

	@pydantic.validate_arguments
	def __call__(self, repository: Repository) -> None:
		del repository[self.item]