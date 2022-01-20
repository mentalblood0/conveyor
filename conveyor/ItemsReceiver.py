from abc import ABCMeta

from . import Item, Repository



class ItemsReceiver(metaclass=ABCMeta):

	input_type: str = 'undefined'
	input_status: str = 'created'

	def __init__(self, repository: Repository, one_call_items_limit: int = 64) -> None:
		self.repository = repository
		self.one_call_items_limit = one_call_items_limit

	def receiveItems(self) -> list[Item]:
		
		result = self.repository.get(self.input_type, self.input_status, limit=self.one_call_items_limit)
		for i in result:
			i.worker = self.__class__.__name__
		
		return result