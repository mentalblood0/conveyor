from abc import ABCMeta, abstractmethod
from typing import Any

from . import OutputProvider



class Creator(metaclass=ABCMeta):

	output_status: str = 'created'

	def __init__(self, output_provider: OutputProvider) -> None:
		self.output_provider = output_provider

	@abstractmethod
	def create(self, data: Any) -> Any:
		pass

	def __call__(self, *args, **kwargs) -> None:

		output_data = self.create(*args, **kwargs)

		return self.output_provider.create(self.output_status, **output_data)



import sys
sys.modules[__name__] = Creator