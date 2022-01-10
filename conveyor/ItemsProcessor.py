from loguru import logger
from abc import ABCMeta, abstractmethod

from . import Item, ItemsReceiver, Transaction



class ItemsProcessor(ItemsReceiver, metaclass=ABCMeta):

	@abstractmethod
	def processItem(self, item: Item) -> Transaction:
		pass

	def __call__(self) -> list:

		result = []

		for i in self.receiveItems():
			
			i_result = self.processItem(i).execute()
			i_info = {
				'id': i.id,
				'chain_id': i.chain_id
			}
			logger.info(f'{self.__class__.__name__} {i_info} => {i_result}')

			result.append(i_result)

		return result