import uuid
import dataclasses
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

		try:
			item = self.create(*args, **kwargs)
		except Exception:
			return 0
		
		return self.repository.create(
			dataclasses.replace(
				item,
				type=self.output_type,
				status=self.output_status,
				chain_id=' '.join([
					str(datetime.utcnow()),
					uuid.uuid4().hex
				])
			)
		)