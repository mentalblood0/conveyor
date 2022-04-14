import dataclasses
from abc import ABCMeta
from copy import deepcopy

from ..core import Item, Processor



class Mover(Processor, metaclass=ABCMeta):

	input_type: str
	input_status: str
	moved_status: str

	possible_output_types: list[str]
	output_status: str

	def transform(self, item: Item) -> list[Item] | Item:
		return []

	def processItem(self, input_item):

		output = self.transform(deepcopy(input_item))
		if type(output) is None:
			return None

		if type(output) == Item:
			output_items = [output]
		elif type(output) == list:
			output_items = output

		if len(output_items):

			if not all(i.type == output_items[0].type for i in output_items):
				raise Exception('output items must be of one type')

			if output_items[0].type not in self.possible_output_types:
				raise Exception(f'output type "{output_items[0].type}" not possible')

			for i in output_items:
				self.repository.create(
					Item(
						type=i.type,
						status=self.output_status,
						chain_id=input_item.chain_id,
						data=i.data,
						metadata=i.metadata
					)
				)

		return self.repository.update(
			dataclasses.replace(
				input_item,
				status=self.moved_status
			)
		)