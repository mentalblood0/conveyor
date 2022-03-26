import time
import uuid
import dataclasses
from abc import ABCMeta, abstractmethod

from .. import Item, Repository



class Creator(metaclass=ABCMeta):

	output_type: str = 'undefined'
	output_status: str = 'created'

	source_type: str | None = None
	source_status: str | None = None
	match_fields: list[str] | None = None

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

		if self.source_type and self.source_status:

			chain_id = self.repository.get(
				type=self.source_type,
				where={
					key: item.metadata[key]
					for key in self.match_fields
				},
				fields=['chain_id']
			).chain_id
		
		else:

			chain_id = ''.join([
				hex(int(time.time() * 10**7))[2:],
				uuid.uuid4().hex
			])

		return self.repository.create(
			dataclasses.replace(
				item,
				type=self.output_type,
				status=self.output_status,
				chain_id=chain_id
			)
		)