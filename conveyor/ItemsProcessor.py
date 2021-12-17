from abc import ABCMeta, abstractmethod

from . import Item, ItemsReceiver



class ItemsProcessor(ItemsReceiver, metaclass=ABCMeta):

	@abstractmethod
	def processItem(self, item: Item):
		pass

	def __call__(self) -> list:
		return [
			self.repository.atomic(self.processItem)(i) 
			for i in self.receiveItems()
		]



import sys
sys.modules[__name__] = ItemsProcessor