from abc import ABCMeta
from copy import deepcopy

from .. import Item, ItemsProcessor



class Mover(ItemsProcessor, metaclass=ABCMeta):

	input_type: str
	input_status: str
	moved_status: str

	output_type: str
	output_status: str
	
	def transform(self, item: Item) -> list[Item]:
		return [item]
	
	def processItem(self, input_item: Item) -> int:

		output_items = self.transform(deepcopy(input_item))
		if type(output_items) != list:
			output_items = [output_items]
		for i in output_items:
			i.type = self.output_type
			i.status = self.output_status
			i.chain_id = input_item.chain_id
			i.worker = self.__class__.__name__
			i.data_digest = input_item.data_digest
			self.repository.create(i)
		
		input_item.status = self.moved_status
		return self.repository.update(self.input_type, input_item.id, input_item)