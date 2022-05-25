import dataclasses
from abc import ABCMeta, abstractmethod

from . import composeChainId
from . import Item, Repository



class Creator(metaclass=ABCMeta):

	output_type: str
	output_status: str

	source_type: str = ''
	source_status: str = ''
	match_fields: list[str] = []

	def __init__(self, repository: Repository) -> None:
		self.repository = repository

	@abstractmethod
	def create(self, *args, **kwargs) -> Item:
		pass

	def handleException(e: Exception, name: str):
		pass

	def __call__(self, *args, **kwargs) -> int:

		try:

			item = self.create(*args, **kwargs)

			if self.source_type and self.source_status:

				try:
					chain_id = self.repository.get(
						type=self.source_type,
						where={
							key: item.metadata[key]
							for key in self.match_fields
						} | (
							{'status': self.source_status}
							if self.source_status
							else {}
						),
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
		
		except Exception as e:
			self.handleException(e, self.__class__.__name__)