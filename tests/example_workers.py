from lxml import etree
from conveyor import Item
from structure_mapper import *
from conveyor.workers import *



class FileSaver(Creator):

	output_type = 'undefined'
	output_status = 'created'

	def create(self, text):
		return Item(
			data=text,
			metadata={
				'message_id': ''
			}
		)


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


class Typer(Mover):

	input_type = 'undefined'
	input_status = 'xml'
	moved_status = 'end'

	possible_output_types = [
		'PersonalizationRequest'
	]
	output_status = 'created'

	def transform(self, item):

		text = item.data
		type = findByYPath('Body/0', text, content_type='tag')

		item.type = type
		item.metadata['message_id'] = findByYPath('MessageID', text)

		return item


class PrintTaskSaver(Creator):

	output_type = 'PrintTask'
	output_status = 'created'

	source_type = 'PersonalizationRequest'
	source_status = 'created'
	match_fields = ['message_id']

	def create(self, text):
		return Item(
			data=text,
			metadata={
				'message_id': findByYPath('MessageID', text)
			}
		)