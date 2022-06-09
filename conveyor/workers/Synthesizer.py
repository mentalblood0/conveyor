import pydantic
import dataclasses
from abc import ABCMeta
from copy import deepcopy

from ..core import Item, Processor



class Synthesizer(Processor, metaclass=ABCMeta):

	moved_status: str
	not_matched_status: str

	output_type: str
	output_status: str

	source_type: str
	match_fields: list[str]
	source_status: str = None

	def transform(self, item: Item, source_item: Item) -> list[Item] | Item:
		return []

	@pydantic.validate_arguments
	def processItem(self, input_item: Item):

		where = {
			key: input_item.metadata[key]
			for key in self.match_fields
		}
		if self.source_status:
			where['status'] = self.source_status

		matched_items = [
			i
			for i in self.repository.get(
				type=self.source_type,
				where=where,
				limit=2
			)
			if not (
				(i.type == input_item.type) and
				(i.status == input_item.status) and
				(i.id == input_item.id)
			)
		]
		if len(matched_items):
			source_item = matched_items[0]
		elif self.not_matched_status is None:
			source_item = None
		else:
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
		if output is None:
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