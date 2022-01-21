from loguru import logger
from abc import ABCMeta, abstractmethod

from . import Item, ItemsReceiver, Transaction



class ItemsProcessor(ItemsReceiver, metaclass=ABCMeta):

	def __init__(self, *args, logs_dir='conveyor_log', **kwargs) -> None:

		super().__init__(*args, **kwargs)
		
		self.logs_dir = logs_dir

	@abstractmethod
	def processItem(self, item: Item) -> Transaction:
		pass

	def __call__(self) -> list:

		result = []

		for i in self.receiveItems():

			try:
				i_transaction = self.processItem(i)
			except Exception as e:
				logger.exception(e)
				continue
			
			if i_transaction != None:
				i_result = i_transaction.execute()
				logger.info(f'{self.__class__.__name__} => {i_result}')
			else:
				i_result = None

			result.append(i_result)

		return result