from abc import ABCMeta

from . import InputProvider, OutputProvider



class Mover(metaclass=ABCMeta):

	input_status: str
	moved_status: str

	output_status: str

	def __init__(self, input_provider: InputProvider, output_provider: OutputProvider) -> None:
		self.input_provider = input_provider
		self.output_provider = output_provider
	
	def transform(self, data: dict) -> dict:
		return data

	def __call__(self) -> dict:

		data = self.input_provider.get(self.input_status)
		if data == None:
			return None
		
		extracted_data = {
			k: v.get()
			for k, v in data.items()
			if k != 'metadata'
		} | {
			'metadata': {
				k: v.get()
				for k, v in data['metadata'].get().items()
			} | {
				'status': self.output_status
			}
		}
		new_data = self.transform(extracted_data)

		result = self.output_provider.create(**new_data)
		data['metadata'].get()['status'].set(self.moved_status)

		return result



import sys
sys.modules[__name__] = Mover