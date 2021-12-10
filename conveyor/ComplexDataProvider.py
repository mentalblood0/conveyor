class ComplexDataProvider:

	def __init__(self, sub_data_providers):
		self.sub_data_providers = sub_data_providers
	
	def __getitem__(self, key):
		return self.sub_data_providers[key]
	
	def keys(self):
		return self.sub_data_providers.keys()
	
	def values(self):
		return self.sub_data_providers.values()
	
	def items(self):
		return self.sub_data_providers.items()



import sys
sys.modules[__name__] = ComplexDataProvider