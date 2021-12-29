from abc import ABCMeta, abstractmethod

from . import Item, ItemsReceiver, Transaction



class ItemsProcessor(ItemsReceiver, metaclass=ABCMeta):

	@abstractmethod
	def processItem(self, item: Item) -> Transaction:
		pass

	def __call__(self) -> list:
		return [
			self.processItem(i).execute()
			for i in self.receiveItems()
		]