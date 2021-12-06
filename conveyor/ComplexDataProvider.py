class ComplexDataProvider:

	def __init__(self, sub_data_providers):
		self.sub_data_providers = sub_data_providers
	
	def __getitem__(self, key):
		return self.sub_data_providers[key]



import sys
sys.modules[__name__] = ComplexDataProvider