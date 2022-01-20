import os
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
	
	def log(self, item, result):

		logger.info(f'{self.__class__.__name__} => {result}')

		# chain_id = item.chain_id.replace(':', '_')

		# file_name = f'{chain_id}.log'
		# file_path = os.path.join(self.logs_dir, file_name)
		# if not os.path.exists(file_path):
		# 	logger.add(
		# 		file_path, 
		# 		filter=lambda r: ('id' in r['extra']) and (r['extra']['id'] == chain_id),
		# 		format='{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{message}</level>'
		# 	)

		# logger.bind(id=f'{chain_id}').info(f'{self.__class__.__name__} => {result}')

	def __call__(self) -> list:

		result = []

		for i in self.receiveItems():

			try:
				i_transaction = self.processItem(i)
			except Exception as e:
				logger.exception(e)
				continue

			i_result = i_transaction.execute()
			self.log(i, i_result)

			result.append(i_result)

		return result