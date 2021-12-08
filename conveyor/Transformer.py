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
			return None

		new_data = self.transform(data)
		if type(new_data) == str:
			new_data = {
				'status': new_data
			}
		elif type(new_data) == dict:
			new_data = {
				k: v
				for k, v in new_data.items()
				if not k in ['id']
			}
		else:
			return None

		if (new_data['status'] == None) or (not new_data['status'] in self.possible_output_statuses):
			return None

		for k, v in new_data.items():
			data['metadata'].get()[k].set(v)

		return new_data['status']



import sys
sys.modules[__name__] = Transformer