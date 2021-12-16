from abc import ABCMeta

from . import Item, ItemRepository



class ItemsReceiver(metaclass=ABCMeta):

	input_type: str = 'undefined'
	input_status: str = 'created'

	def __init__(self, repository: ItemRepository, one_call_items_limit: int = None) -> None:
		self.repository = repository
		self.one_call_items_limit = one_call_items_limit

	def receiveItems(self) -> list[Item]:
		return self.repository.get(self.input_type, self.input_status, limit=self.one_call_items_limit)



import sys
sys.modules[__name__] = ItemsReceiver