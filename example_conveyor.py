from lxml import etree
from conveyor import Transformer



class isXml(Transformer):

	input = {
		'type': 'PersonalizationRequest',
		'state': 'saved'
	}
	possible_outputs = [{
		'type': 'PersonalizationRequest',
		'state': 'xml'
	}, {
		'type': 'PersonalizationRequest',
		'state': 'not xml'
	}]

	def transform(self, data):

		file_content = data['file'].get()
		
		try:
			etree.fromstring(file_content)
			return {
				'type': 'PersonalizationRequest',
				'state': 'xml'
			}
		except etree.XMLSyntaxError:
			return {
				'type': 'PersonalizationRequest',
				'state': 'not xml'
			}



import sys
sys.modules[__name__] = isXml