from abc import ABCMeta, abstractmethod



class DataProvider(metaclass=ABCMeta):

	@abstractmethod
	def get(self):
		pass

	@abstractmethod
	def set(self, new_data):
		pass



import sys
sys.modules[__name__] = DataProvider