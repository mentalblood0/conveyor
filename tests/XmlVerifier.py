from lxml import etree
from conveyor.workers import Transformer



class XmlVerifier(Transformer):

	input_type = 'undefined'
	input_status = 'created'

	possible_output_statuses = [
		'xml',
		'not xml'
	]

	def transform(self, item):

		try:
			etree.fromstring(item.data)
			return 'xml'
		except etree.XMLSyntaxError:
			return 'not xml'



import sys
sys.modules[__name__] = XmlVerifier