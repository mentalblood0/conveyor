from abc import ABCMeta, abstractmethod

from .. import Item, Processor



class Transformer(Processor, metaclass=ABCMeta):

	input_type: str
	input_status: str

	possible_output_statuses: list[str]

	@abstractmethod
	def transform(self, item: Item) -> Item:
		pass
	
	def processItem(self, input_item: Item) -> int | None:

		output_item = self.transform(input_item)
		if output_item == None:
			return None
		
		if type(output_item) == str:
			output_status = output_item
			output_item = input_item
			output_item.status = output_status

		if not output_item.status in self.possible_output_statuses:
			return None
		
		output_item.data_digest = input_item.data_digest
		
		return self.repository.update(self.input_type, input_item.id, output_item)