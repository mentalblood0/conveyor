from abc import ABCMeta

from . import InputProvider, OutputProvider



class Mover(metaclass=ABCMeta):

	input_status: str
	output_status: str

	def __init__(self, input_provider: InputProvider, output_provider: OutputProvider) -> None:
		self.input_provider = input_provider
		self.output_provider = output_provider

	def __call__(self) -> dict:

		data = self.input_provider.get(self.input_status)
		if data == None:
			return None
		
		return self.output_provider.create(**{
			k: v.get()
			for k, v in data.items()
		})



import sys
sys.modules[__name__] = Mover