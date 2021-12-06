from lxml import etree
from conveyor import Transformer



class isXml(Transformer):

	item_type = 'PersonalizationRequest'

	input_state = 'saved'
	possible_output_states = [
		'xml',
		'not xml'
	]

	def transform(self, data):

		file_content = data['file'].get()
		
		try:
			etree.fromstring(file_content)
			return 'xml'
		except etree.XMLSyntaxError:
			return 'not xml'



import sys
sys.modules[__name__] = isXml