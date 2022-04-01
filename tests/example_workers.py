import dataclasses
from conveyor import Item

from conveyor.workers import *
from conveyor.core import Creator



class Saver(Creator):

	output_type = 'undefined'
	output_status = 'created'

	def create(self, text):
		return Item(
			data=text,
			metadata={
				'square': -1
			}
		)


class Verifier(Transformer):

	input_type = 'undefined'
	input_status = 'created'

	possible_output_statuses = [
		'valid',
		'invalid'
	]

	def transform(self, item):

		try:
			int(item.data)
		except ValueError:
			return 'invalid'

		return dataclasses.replace(
			item,
			status='valid',
			metadata={
				'square': int(item.data) ** 2
			}
		)


class Typer(Mover):

	input_type = 'undefined'
	input_status = 'valid'
	moved_status = 'typed'

	possible_output_types = [
		'even',
		'odd'
	]
	output_status = 'created'

	def transform(self, item):
		return dataclasses.replace(
			item,
			type='odd' if int(item.data) % 2 else 'even'
		)


class AnotherSaver(Creator):

	output_type = 'another'
	output_status = 'created'

	source_type = 'odd'
	source_status = 'created'
	match_fields = ['square']

	def create(self, text):
		return Item(
			data=text,
			metadata={
				'square': int(text) ** 2
			}
		)