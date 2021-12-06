from abc import ABCMeta, abstractmethod



class OutputProvider(metaclass=ABCMeta):

	@abstractmethod
	def set(self, new_data):
		pass



import sys
sys.modules[__name__] = OutputProvider