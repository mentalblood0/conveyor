from typing import Callable, Any
from abc import ABCMeta, abstractmethod

from . import Item



class Repository(metaclass=ABCMeta):

	@abstractmethod
	def create(self, item: Item) -> int:
		pass

	@abstractmethod
	def reserve(self, type: str, status: str, id: str, limit: int) -> int:
		pass

	@abstractmethod
	def unreserve(self, type: str, status: str, id: str) -> int:
		pass

	@abstractmethod
	def get(self, type: str, where: dict[str, Any]=None, where_not: dict[str, Any]=None, fields: list[str]=None, limit: int=1, reserved_by: str=None) -> list[Item]:
		pass

	@abstractmethod
	def update(self, item: Item) -> int:
		pass

	@abstractmethod
	def delete(self, type: str, id: str) -> int:
		pass

	@abstractmethod
	def transaction(self) -> Callable[[Callable], Callable]:
		pass
