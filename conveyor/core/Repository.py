from typing import Callable
from abc import ABCMeta, abstractmethod

from . import Item



class Repository(metaclass=ABCMeta):

	@abstractmethod
	def create(self, item: Item) -> int:
		pass

	@abstractmethod
	def get(self, type: str, where: dict[str, any]=None, fields: list[str]=None, limit: int=1) -> list[Item]:
		pass

	@abstractmethod
	def update(self, type: str, item: Item) -> int:
		pass

	@abstractmethod
	def delete(self, type: str, id: str) -> int:
		pass

	@abstractmethod
	def transaction(self) -> Callable[[Callable], Callable]:
		pass
