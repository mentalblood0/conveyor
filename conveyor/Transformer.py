from abc import ABCMeta, abstractmethod

from . import InputProvider, ComplexDataProvider



class Transformer(metaclass=ABCMeta):

	item_type: str
	input_state: str
	possible_output_states: list

	def __init__(self, input_provider: InputProvider) -> None:
		self.input_provider = input_provider

	@abstractmethod
	def transform(self, data: ComplexDataProvider) -> dict:
		pass

	def __call__(self) -> dict:

		data = self.input_provider.get(self.input_state)
		if data == None:
			raise Exception('Input provider returned None')

		new_state = self.transform(data)
		if (new_state == None) or (not new_state in self.possible_output_states):
			return None
		else:
			data['state'].set(new_state)

		return new_state



import sys
sys.modules[__name__] = Transformer