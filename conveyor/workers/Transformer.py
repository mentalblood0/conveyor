from abc import ABCMeta, abstractmethod

from .. import Item, ItemsProcessor



class Transformer(ItemsProcessor, metaclass=ABCMeta):

	input_type: str
	input_status: str

	possible_output_statuses: list[str]

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
		
		return self.repository.update(self.input_type, input_item.id, output_item)