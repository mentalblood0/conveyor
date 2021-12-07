from conveyor import Creator
from growing_tree_base import *



class FileSaver(Creator):

	output_status = 'created'

	def create(self, text):
		return {
			'text': text,
			'metadata': {}
		}



import sys
sys.modules[__name__] = FileSaver