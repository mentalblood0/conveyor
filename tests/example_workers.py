import dataclasses
from lxml import etree
from conveyor import Item
from structure_mapper import *
from conveyor.workers import Creator, Transformer, Mover, Linker



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


class Typer(Transformer):

	input_type = 'undefined'
	input_status = 'xml'

	possible_output_statuses = [
		'PersonalizationRequest'
	]

	def transform(self, item):

		text = item.data
		type = findByYPath('Body/0', text, content_type='tag')
		
		if type in self.possible_output_statuses:
			item.status = type
			item.metadata['message_id'] = findByYPath('MessageID', text)
			return item
		else:
			return None


class PersonalizationRequestToCreatedMover(Mover):

	input_type = 'undefined'
	input_status = 'PersonalizationRequest'
	moved_status = 'end'

	output_type = 'PersonalizationRequest'
	output_status = 'created'

	def transform(self, item):
		return [item]


class PrintTaskSaver(Creator):

	output_type = 'PrintTask'
	output_status = 'created'

	def create(self, text):
		return Item(
			data=text,
			metadata={
				'message_id': findByYPath('MessageID', text)
			}
		)