from lxml import etree
from conveyor import Transformer



class isXml(Transformer):

	item_type = 'PersonalizationRequest'

	input_status = 'created'
	possible_output_statuss = [
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