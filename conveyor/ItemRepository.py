from abc import ABCMeta, abstractmethod

from . import Item



class ItemRepository(metaclass=ABCMeta):

	@abstractmethod
	def save(self, item: Item):
		pass

	@abstractmethod
	def get(self, type: str, status: Item, limit=None) -> list[Item]:
		pass

	@abstractmethod
	def set(self, type: str, id: str, item: Item):
		pass

	@abstractmethod
	def delete(self, id: str):
		pass
	
	# property that should return decorator
	@abstractmethod
	def atomic(self):
		pass



import sys
sys.modules[__name__] = ItemRepository