import dataclasses
from abc import ABCMeta, abstractmethod

from .. import Item, Processor



class Transformer(Processor, metaclass=ABCMeta):

	input_type: str
	input_status: str

	possible_output_statuses: list[str]

	@abstractmethod
	def transform(self, item: Item) -> Item | str:
		pass

	def processItem(self, input_item: Item) -> int | None:

		output = self.transform(input_item)

		if output == None:
			return None

		elif type(output) == Item:

			output_status = output.status
			if not output_status in self.possible_output_statuses:
				return None

			output_item = dataclasses.replace(
				input_item,
				status=output_status,
				metadata=output.metadata
			)

		elif type(output) == str:
			
			output_status = output_item
			if not output_status in self.possible_output_statuses:
				return None

			output_item = dataclasses.replace(
				input_item,
				status=output_status
			)

		return self.repository.update(self.input_type, input_item.id, output_item)