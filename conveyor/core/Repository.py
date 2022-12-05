import abc
import typing

from . import Item, Word



class Repository(metaclass=abc.ABCMeta):

	@abc.abstractmethod
	def create(self, item: Item) -> None:
		pass

	@abc.abstractmethod
	def reserve(self, type: str, status: str, id: str, limit: int | None=None) -> None:
		pass

	@abc.abstractmethod
	def unreserve(self, item: Item) -> None:
		pass

	@abc.abstractmethod
	def get(self, type: str, where: dict[Word, Item.Value] | None=None, limit: int | None=1, reserved: str | None=None) -> list[Item]:
		pass

	@abc.abstractmethod
	def update(self, old: Item, new: Item) -> None:
		pass

	@abc.abstractmethod
	def delete(self, item: Item) -> None:
		pass

	@abc.abstractmethod
	def transaction(self, f: typing.Callable) -> typing.Callable:
		pass
