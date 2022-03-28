from abc import ABCMeta, abstractmethod

from .. import Repository



class Destroyer(metaclass=ABCMeta):

	input_type: str
	input_status: str

	def __init__(self, repository: Repository, one_call_items_limit: int=64) -> None:
		self.repository = repository
		self.one_call_items_limit = one_call_items_limit

	def __call__(self) -> list[int]:
		return [
			self.repository.delete(
				type=self.input_type,
				id=item.id
			)
			for item in self.repository.get(
				type=self.input_type,
				where={'status': self.input_status},
				fields=['id'],
				limit=self.one_call_items_limit
			)
		]