from abc import ABCMeta, abstractmethod



class Transformer(metaclass=ABCMeta):

	def __init__(self, input_provider, output_provider):
		self.input_provider = input_provider
		self.output_provider = output_provider

	@abstractmethod
	def transform(self, input):
		return input

	def __call__(self):

		input = self.input_provider.get()
		output = self.transform(input)
		self.output_provider.set(output)
		
		self.input_provider.delete()



import sys
sys.modules[__name__] = Transformer