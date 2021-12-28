from abc import ABCMeta, abstractmethod



class Command(metaclass=ABCMeta):

	@abstractmethod
	def __call__(self, *args, **kwargs):
		pass

	@abstractmethod
	def revert(self, *args, **kwargs):
		pass