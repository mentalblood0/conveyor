import uuid
from datetime import datetime
from abc import ABCMeta, abstractmethod

from .. import OutputProvider



class Creator(metaclass=ABCMeta):

	output_status: str = 'created'

	def __init__(self, output_provider: OutputProvider) -> None:
		self.output_provider = output_provider

	@abstractmethod
	def create(self, *args, **kwargs) -> dict:
		pass

	def __call__(self, *args, **kwargs) -> None:

		output_data = self.create(*args, **kwargs)
		output_data['metadata'] |= {
			'status': self.output_status,
			'chain_id': ' '.join([
				str(datetime.now()),
				uuid.uuid4().hex
			])
		}
		output_data['metadata']['status'] = self.output_status

		return self.output_provider.create(**output_data)



import sys
sys.modules[__name__] = Creator