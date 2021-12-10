from lxml import etree
from conveyor.workers import Transformer



class XmlVerifier(Transformer):

	input_status = 'created'
	possible_output_statuses = [
		'xml',
		'not xml'
	]

	def transform(self, data):

		file_content = data['text'].get()
		
		try:
			etree.fromstring(file_content)
			return 'xml'
		except etree.XMLSyntaxError:
			return 'not xml'



import sys
sys.modules[__name__] = XmlVerifier