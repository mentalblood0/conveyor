import pydantic
import dataclasses
from abc import ABCMeta
from copy import deepcopy

from ..core import Item, Processor



class Mover(Processor, metaclass=ABCMeta):

	moved_status: str

	possible_output_types: list[str]
	output_status: str

	def transform(self, item: Item) -> list[Item] | Item:
		return []

	@pydantic.validate_arguments
	def processItem(self, input_item: Item):

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

			for o in output_items:
				self.repository.create(
					item=Item(
						type=o.type,
						status=self.output_status,
						chain_id=input_item.chain_id,
						data=o.data,
						metadata=o.metadata
					),
					ref=input_item
				)

		return self.repository.update(
			dataclasses.replace(
				input_item,
				status=self.moved_status
			)
		)