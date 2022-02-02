from abc import ABCMeta

from .. import Item, Processor



class Destroyer(Processor, metaclass=ABCMeta):

	input_type: str
	input_status: str
	
	def processItem(self, item: Item) -> int:
		return self.repository.delete(self.input_type, item.id)