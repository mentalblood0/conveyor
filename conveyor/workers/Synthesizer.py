import dataclasses
from abc import ABCMeta
from copy import deepcopy

from ..core import Item, Processor, composeChainId



class Synthesizer(Processor, metaclass=ABCMeta):

	input_type: str
	input_status: str
	moved_status: str
	not_matched_status: str

	output_type: str
	output_status: str

	source_type: str = ''
	source_status: str = ''
	match_fields: list[str] = dataclasses.field(default_factory=list)

	def transform(self, item: Item, source_item: Item) -> list[Item] | Item:
		return []

	def processItem(self, input_item):

		try:
			source_item = self.repository.get(
				type=self.source_type,
				where={
					key: input_item.metadata[key]
					for key in self.match_fields
				}
			)[0]

		except IndexError:
			return self.repository.update(
				dataclasses.replace(
					input_item,
					status=self.not_matched_status
				)
			)

		output = self.transform(
			deepcopy(input_item), 
			deepcopy(source_item)
		)
		if type(output) is None:
			return

		if type(output) == Item:
			output_items = [output]
		elif type(output) == list:
			output_items = output

		for i in output_items:
			self.repository.create(
				Item(
					type=self.output_type,
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