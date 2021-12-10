from abc import ABCMeta, abstractmethod



class OutputProvider(metaclass=ABCMeta):

	@abstractmethod
	def set(self, new_data):
		pass

	@abstractmethod
	def create(self, *args, **kwargs):
		pass

	@abstractmethod
	def delete(self):
		pass



import sys
sys.modules[__name__] = OutputProvider