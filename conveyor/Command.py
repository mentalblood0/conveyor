from typing import Any
from abc import ABCMeta, abstractmethod



class Command(metaclass=ABCMeta):

	args: list
	kwargs: dict
	result: Any

	def __init__(self):
		self.args = []
		self.kwargs = {}
		self.result = None
	
	def __call__(self, *args, **kwargs):

		self.args = args
		self.kwargs = kwargs

		self.result = self.execute(*self.args, **self.kwargs)
		return self.result
	
	@abstractmethod
	def execute(self, *args, **kwargs):
		pass

	def revert(self):

		result = self._revert(*self.args, **self.kwargs, result=self.result)
		
		self.args = []
		self.kwargs = {}
		self.result = None

		return result

	@abstractmethod
	def _revert(self, *args, **kwargs):
		pass