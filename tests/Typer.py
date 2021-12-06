from lxml import etree
from conveyor import Transformer
from structure_mapper import findByYPath



class Typer(Transformer):

	item_type = 'undefined'

	input_status = 'xml'
	possible_output_statuses = [
		'PersonalizationRequest'
	]

	def transform(self, data):

		text = data['file'].get()
		type = findByYPath('Body/0', text, content_type='tag')
		
		if type in self.possible_output_statuses:
			return type
		else:
			return None



import sys
sys.modules[__name__] = Typer