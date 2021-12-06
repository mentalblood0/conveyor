from lxml import etree
from conveyor import Transformer



class XmlVerifier(Transformer):

	item_type = 'undefined'

	input_status = 'created'
	possible_output_statuses = [
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
sys.modules[__name__] = XmlVerifier