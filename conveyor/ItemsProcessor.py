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

		chain_id = item.chain_id.replace(':', '_').replace(' ', '_')

		file_name = f'{chain_id}.log'
		file_path = os.path.join(self.logs_dir, file_name)
		if not os.path.exists(file_path):
			logger.add(
				file_path, 
				filter=lambda r: r['extra']['id'] == chain_id,
				format='{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{message}</level>'
			)

		logger.bind(id=f'{chain_id}').info(f'{self.__class__.__name__} => {result}')

	def __call__(self) -> list:

		result = []

		for i in self.receiveItems():
			
			i_result = self.processItem(i).execute()
			self.log(i, i_result)

			result.append(i_result)

		return result