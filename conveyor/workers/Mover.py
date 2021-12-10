from abc import ABCMeta

from .. import Item, ItemRepository



class Mover(metaclass=ABCMeta):

	input_type: str
	input_status: str
	moved_status: str

	output_type: str
	output_status: str

	def __init__(self, repository: ItemRepository) -> None:
		self.repository = repository
	
	def transform(self, item: Item) -> list[Item]:
		return [item]

	def __call__(self) -> Item:

		input_item = self.repository.get(self.input_type, self.input_status)
		if input_item == None:
			return None

		output_items = self.transform(input_item)
		for i in output_items:
			i.type = self.output_type
			i.status = self.output_status
			i.chain_id = input_item.chain_id
			self.repository.save(i)
		
		input_item.status = self.moved_status
		self.repository.set(self.input_type, input_item.id, input_item)
		
		return output_items



import sys
sys.modules[__name__] = Mover