from abc import ABCMeta

from .. import Item, ItemRepository



class Destroyer(metaclass=ABCMeta):

	input_type: str
	input_status: str

	def __init__(self, repository: ItemRepository) -> None:
		self.repository = repository
	
	def processItem(self, item: Item) -> int:
		return self.repository.delete(self.input_type, item.id)

	def __call__(self) -> list[int]:

		items = self.repository.get(self.input_type, self.input_status)

		return [self.processItem(i) for i in items]



import sys
sys.modules[__name__] = Destroyer