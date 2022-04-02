import dataclasses
from copy import deepcopy
from abc import ABCMeta, abstractmethod

from ..core import Item, Worker



class Transformer(Worker, metaclass=ABCMeta):

	input_type: str
	input_status: str

	possible_output_statuses: list[str]

	@abstractmethod
	def transform(self, item: Item) -> Item | str:
		pass

	def processItem(self, input_item):

		output = self.transform(deepcopy(input_item))

		if output == None:
			return None

		elif type(output) == Item:
			new = {
				'status': output.status,
				'metadata': output.metadata
			}
		elif type(output) == str:
			new = {
				'status': output
			}

		if not new['status'] in self.possible_output_statuses:
			return None

		return self.repository.update(dataclasses.replace(input_item, **new))