from abc import ABCMeta, abstractmethod



class Command(metaclass=ABCMeta):

	args: list
	kwargs: dict
	result = None

	def __init__(self):
		self.args = []
		self.kwargs = {}
	
	def __call__(self, *args, **kwargs):

		self.args = args
		self.kwargs = kwargs

		self.result = self.execute(*self.args, **self.kwargs)
		return self.result
	
	@abstractmethod
	def execute(self, *args, **kwargs):
		pass

	def revert(self):
		return self.revert(*self.args, result=self.result, **self.kwargs)

	@abstractmethod
	def _revert(self, *args, **kwargs):
		pass