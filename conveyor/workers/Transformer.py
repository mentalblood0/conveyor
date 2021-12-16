from abc import ABCMeta, abstractmethod

from .. import Item, ItemRepository



class Transformer(metaclass=ABCMeta):

	input_type: str
	input_status: str

	possible_output_statuses: list[str]

	def __init__(self, repository: ItemRepository) -> None:
		self.repository = repository

	@abstractmethod
	def transform(self, item: Item) -> Item:
		pass
	
	def processItem(self, input_item: Item) -> int:

		output_item = self.transform(input_item)
		if type(output_item) == str:
			output_status = output_item
			output_item = input_item
			output_item.status = output_status

		if not output_item.status in self.possible_output_statuses:
			return None
		
		return self.repository.set(self.input_type, input_item.id, output_item)

	def __call__(self) -> list[int]:

		input_items = self.repository.get(self.input_type, self.input_status)
		
		return [self.processItem(i) for i in input_items]



import sys
sys.modules[__name__] = Transformer