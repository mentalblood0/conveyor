from abc import ABCMeta

from . import Item, Repository



class Receiver(metaclass=ABCMeta):

	input_type: str
	input_status: str

	def __init__(self, repository: Repository, one_call_items_limit: int = 64) -> None:
		self.repository = repository
		self.one_call_items_limit = one_call_items_limit

	def receiveItems(self) -> list[Item]:
		return self.repository.get(
			self.input_type,
			where={'status': self.input_status},
			limit=self.one_call_items_limit
		)