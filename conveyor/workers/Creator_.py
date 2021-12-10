import uuid
from datetime import datetime
from abc import ABCMeta, abstractmethod

from .. import Item, ItemRepository



class Creator(metaclass=ABCMeta):

	output_type: str = 'undefined'
	output_status: str = 'created'

	def __init__(self, repository: ItemRepository) -> None:
		self.repository = repository

	@abstractmethod
	def create(self, *args, **kwargs) -> dict:
		pass

	def __call__(self, *args, **kwargs) -> None:

		item_args = self.create(*args, **kwargs) | {
			'chain_id': ' '.join([
				str(datetime.now()),
				uuid.uuid4().hex
			])
		}
		item = Item(**item_args)

		return self.repository.save(item)



import sys
sys.modules[__name__] = Creator