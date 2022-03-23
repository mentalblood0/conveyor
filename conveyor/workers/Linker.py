import dataclasses
from copy import deepcopy
from abc import ABCMeta, abstractmethod

from .. import Item, Processor



class Linker(Processor, metaclass=ABCMeta):

	unlinked_type: str
	unlinked_status: str

	source_type: str
	source_status: str

	linked_status: str='linked'

	@abstractmethod
	def link(self, item: Item) -> Item:
		pass

	def processItem(self, unlinked_item: Item) -> int | None:

		source_item = self.link(deepcopy(unlinked_item))
		if source_item == None:
			return None

		chain_id = self.repository.get(
			self.source_type,
			self.source_item.metadata | {
				'status': self.source_status
			},
			['chain_id']
		)

		linked_item = dataclasses.update(
			unlinked_item,
			chain_id=chain_id,
			status=self.linked_status
		)

		return self.repository.update(self.unlinked_type, unlinked_item.id, linked_item)