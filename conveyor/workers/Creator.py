import time
import uuid
import dataclasses
from abc import ABCMeta, abstractmethod

from ..core import Item, Repository



def composeChainId():
	return ''.join([
		hex(int(time.time() * 10**7))[2:],
		uuid.uuid4().hex
	])


class Creator(metaclass=ABCMeta):

	output_type: str
	output_status: str

	source_type: str = ''
	source_status: str = ''
	match_fields: list[str] = dataclasses.field(default_factory=list)

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

			try:
				chain_id = self.repository.get(
					type=self.source_type,
					where={
						key: item.metadata[key]
						for key in self.match_fields
					},
					fields=['chain_id']
				)[0].chain_id

			except IndexError:
				chain_id = composeChainId()
		
		else:
			chain_id = composeChainId()

		return self.repository.create(
			dataclasses.replace(
				item,
				type=self.output_type,
				status=self.output_status,
				chain_id=chain_id
			)
		)