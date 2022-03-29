import dataclasses
from abc import ABCMeta
from copy import deepcopy

from .. import Item, Processor



class Mover(Processor, metaclass=ABCMeta):

	input_type: str
	input_status: str
	moved_status: str

	output_type: str
	output_status: str

	def transform(self, item: Item) -> list[Item] | Item:
		return [item]

	def processItem(self, input_item: Item) -> int:

		output = self.transform(deepcopy(input_item))

		if type(output) == list:
			output_items = output
		elif type(output) == Item:
			output_items = [output]

		for i in output_items:
			self.repository.create(
				dataclasses.replace(
					i,
					type=self.output_type,
					status=self.output_status,
					chain_id=input_item.chain_id
				)
			)

		return self.repository.update(
			self.input_type,
			input_item.id,
			dataclasses.replace(
				input_item,
				status=self.moved_status
			)
		)