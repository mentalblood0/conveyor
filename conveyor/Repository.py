from typing import Callable
from abc import ABCMeta, abstractmethod

from . import Item



class Repository(metaclass=ABCMeta):

	@abstractmethod
	def create(self, item: Item) -> int:
		pass

	@abstractmethod
	def get(self, type: str, status: Item, limit=None) -> list[Item]:
		pass

	@abstractmethod
	def update(self, type: str, id: str, item: Item) -> int:
		pass

	@abstractmethod
	def delete(self, id: str) -> int:
		pass
	
	@abstractmethod
	def transaction(self) -> Callable[[Callable], Callable]:
		pass