from abc import ABCMeta, abstractmethod

from .. import Item, ItemRepository



class Transformer(metaclass=ABCMeta):

	input_type: str
	input_status: str

	possible_output_statuses: list[str]

	def __init__(self, repository: ItemRepository) -> None:
		self.repository = repository

	@abstractmethod
	def transform(self, item: Item) -> str:
		pass

	def __call__(self) -> str:

		input_item = self.repository.get(self.input_type, self.input_status)
		if input_item == None:
			return None
		
		output_status = self.transform(input_item)
		if not output_status in self.possible_output_statuses:
			return None
		
		return self.repository.setStatus(self.input_type, input_item.id, output_status)



import sys
sys.modules[__name__] = Transformer