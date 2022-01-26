from loguru import logger
from abc import ABCMeta, abstractmethod

from . import Item, ItemsReceiver



class ItemsProcessor(ItemsReceiver, metaclass=ABCMeta):

	@abstractmethod
	def processItem(self, item: Item):
		pass

	def __call__(self) -> list:

		result = []

		for i in self.receiveItems():
			try:
				result.append(
					self.repository.atomic(self.processItem)(i)
				)
			except Exception as e:
				logger.error(e)
				continue
		
		return result