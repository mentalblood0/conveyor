import dataclasses
from copy import deepcopy
from abc import ABCMeta, abstractmethod

from .. import Item, Processor



class Linker(Processor, metaclass=ABCMeta):

	input_type: str
	input_status: str

	source_type: str
	source_status: str

	output_status: str='linked'

	@abstractmethod
	def link(self, item: Item) -> Item:
		pass

	def processItem(self, input_item: Item) -> int | None:

		source_item = self.link(deepcopy(input_item))
		if source_item == None:
			return None

		chain_id = self.repository.get(
			self.source_type,
			source_item.metadata | {
				'status': self.source_status
			},
			['chain_id']
		).chain_id

		output_item = dataclasses.replace(
			input_item,
			chain_id=chain_id,
			status=self.output_status
		)

		return self.repository.update(self.input_type, input_item.id, output_item)