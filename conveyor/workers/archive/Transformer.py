import pydantic
import dataclasses
from copy import deepcopy
from abc import ABCMeta, abstractmethod

from ..core import Item, Processor



class Transformer(Processor, metaclass=ABCMeta):

	possible_output_statuses: list[str]

	@abstractmethod
	def transform(self, item: Item) -> Item | str:
		pass

	@pydantic.validate_arguments
	def processItem(self, input_item: Item):

		if (output := self.transform(deepcopy(input_item))) is None:
			return None

		if type(output) == Item:
			new = {
				'status': output.status,
				'metadata': output.metadata
			}
		elif type(output) == str:
			new = {
				'status': output
			}

		if new['status'] not in self.possible_output_statuses:
			return None

		return self.repository.update(dataclasses.replace(input_item, **new))