from abc import ABCMeta, abstractmethod

from .. import Item, ItemRepository



class Transformer(metaclass=ABCMeta):

	input_type: str
	input_status: str

	output_type: str
	possible_output_statuses: list

	def __init__(self, repository: ItemRepository) -> None:
		self.repository = repository

	@abstractmethod
	def transform(self, item: Item) -> Item:
		pass

	def __call__(self) -> Item:

		input_item = self.repository.get(self.input_type, self.input_status)
		if input_item == None:
			return None
		
		output_item = self.transform(input_item)
		output_item.type = self.output_type
		output_item.status = self.output_status

		return output_item



import sys
sys.modules[__name__] = Transformer