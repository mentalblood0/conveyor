from abc import ABCMeta, abstractmethod

from . import InputProvider, ComplexDataProvider



class Transformer(metaclass=ABCMeta):

	input_status: str
	possible_output_statuses: list

	def __init__(self, input_provider: InputProvider) -> None:
		self.input_provider = input_provider

	@abstractmethod
	def transform(self, data: ComplexDataProvider) -> dict:
		pass

	def __call__(self) -> dict:

		data = self.input_provider.get(self.input_status)
		if data == None:
			raise Exception('Input provider returned None')

		new_status = self.transform(data)
		if (new_status == None) or (not new_status in self.possible_output_statuses):
			return None
		else:
			data['status'].set(new_status)

		return new_status



import sys
sys.modules[__name__] = Transformer