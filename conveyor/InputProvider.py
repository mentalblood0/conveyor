from abc import ABCMeta, abstractmethod



class InputProvider(metaclass=ABCMeta):

	@abstractmethod
	def get(self):
		pass



import sys
sys.modules[__name__] = InputProvider