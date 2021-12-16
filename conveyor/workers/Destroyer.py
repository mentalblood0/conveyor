from abc import ABCMeta

from .. import Item, ItemsProcessor



class Destroyer(ItemsProcessor, metaclass=ABCMeta):

	input_type: str
	input_status: str
	
	def processItem(self, item: Item) -> int:
		return self.repository.delete(self.input_type, item.id)



import sys
sys.modules[__name__] = Destroyer