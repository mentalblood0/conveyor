import pydantic

from ..core import Processor, Item



class Destroyer(Processor):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.receive_fields = ['id']

	@pydantic.validate_arguments
	def processItem(self, item: Item):
		return self.repository.delete(item.type, item.id)