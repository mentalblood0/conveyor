from . import InputProvider



class ComplexInputProvider:

	def __init__(self, sub_input_providers):
		self.sub_input_providers = sub_input_providers
	
	def __getitem__(self, key):
		return self.sub_input_providers[key]



import sys
sys.modules[__name__] = ComplexInputProvider