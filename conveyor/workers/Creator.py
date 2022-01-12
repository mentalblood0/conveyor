import uuid
from datetime import datetime
from abc import ABCMeta, abstractmethod

from .. import Item, Repository



class Creator(metaclass=ABCMeta):

	output_type: str = 'undefined'
	output_status: str = 'created'

	def __init__(self, repository: Repository) -> None:
		self.repository = repository

	@abstractmethod
	def create(self, *args, **kwargs) -> Item:
		pass

	def __call__(self, *args, **kwargs) -> int:

		item = self.create(*args, **kwargs)
		item.type = self.output_type
		item.status = self.output_status
		item.chain_id = ' '.join([
			str(datetime.utcnow()),
			uuid.uuid4().hex
		])
		item.worker = self.__class__.__name__
		
		return self.repository.transaction().create(item).execute()