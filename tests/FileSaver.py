from conveyor import Item
from conveyor.workers import Creator



class FileSaver(Creator):

	output_type = 'undefined'
	output_status = 'created'

	def create(self, text):
		return Item(
			data=text,
			metadata={}
		)



import sys
sys.modules[__name__] = FileSaver