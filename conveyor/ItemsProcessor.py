from loguru import logger
from abc import ABCMeta, abstractmethod

from . import Item, ItemsReceiver



class ItemsProcessor(ItemsReceiver, metaclass=ABCMeta):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.processItem = self.repository.transaction(self.processItem)

	@abstractmethod
	def processItem(self, item: Item):
		pass

	def __call__(self) -> list:

		result = []

		for i in self.receiveItems():
			try:
				i_result = self.processItem(i)
				result.append(i_result)
				logger.info(f'{self.__class__.__name__} => {i_result}')
			except Exception as e:
				logger.error(e)
				continue
		
		return result