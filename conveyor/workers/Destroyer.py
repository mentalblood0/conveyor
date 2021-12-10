from abc import ABCMeta

from .. import InputProvider



class Destroyer(metaclass=ABCMeta):

	input_status: str

	def __init__(self, inpute_provider: InputProvider) -> None:
		self.inpute_provider = inpute_provider

	def __call__(self) -> set:

		data = self.inpute_provider.get(self.input_status)
		if data == None:
			return None

		for sub_data in data.values():
			sub_data.delete()

		return data.keys()



import sys
sys.modules[__name__] = Destroyer