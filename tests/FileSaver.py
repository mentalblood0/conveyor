from conveyor.workers import Creator



class FileSaver(Creator):

	output_status = 'created'

	def create(self, text):
		return {
			'text': text,
			'metadata': {}
		}



import sys
sys.modules[__name__] = FileSaver