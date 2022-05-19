from ..core import Processor



class Destroyer(Processor):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.receive_fields = ['id']

	def processItem(self, item):
		return self.repository.delete(item.type, item.id)