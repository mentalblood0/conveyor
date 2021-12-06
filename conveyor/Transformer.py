from abc import ABCMeta, abstractmethod

from . import InputProvider, OutputProvider, ComplexDataProvider



def matchDict(d, pattern):
	return all([
		(k in d) and (d[k] == pattern[k])
		for k in pattern.keys()
	])


class Transformer(metaclass=ABCMeta):

	input = {}
	possible_outputs = []

	def __init__(self, input_provider: InputProvider, output_provider: OutputProvider):
		self.input_provider = input_provider
		self.output_provider = output_provider

	@abstractmethod
	def transform(self, data: ComplexDataProvider):
		pass

	def __call__(self):

		input = self.input_provider.get(match=self.input)
		output = self.transform(input)

		if (output == None) or not any([
			matchDict(output, p)
			for p in self.possible_outputs
		]):
			return None
		else:
			self.output_provider.set(output)
		
		self.input_provider.delete()
		
		return output



import sys
sys.modules[__name__] = Transformer