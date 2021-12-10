from abc import ABCMeta

from .. import ItemRepository



class Destroyer(metaclass=ABCMeta):

	input_type: str
	input_status: str

	def __init__(self, repository: ItemRepository) -> None:
		self.repository = repository

	def __call__(self) -> int:

		item = self.repository.get(self.input_type, self.input_status)
		if not item:
			return None

		return self.repository.delete(self.input_type, item.id)



import sys
sys.modules[__name__] = Destroyer