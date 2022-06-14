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

	def handleException(self, _: Item, e: Exception, name: str):
		pass

	def handleNoException(self, item: Item):
		pass

	@property
	def name(self):
		return self.__class__.__name__

	def __call__(self, *args, **kwargs) -> int:

		try:

			item = self.create(*args, **kwargs)

			if self.source_type:

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

				except:
					chain_id = composeChainId()
			
			else:
				chain_id = composeChainId()

			result = self.repository.create(
				dataclasses.replace(
					item,
					type=self.output_type,
					status=self.output_status,
					chain_id=chain_id
				)
			)
			self.handleNoException(item)
			return result
		
		except Exception as e:
			self.handleException(Item(type=self.output_type, status=self.output_status), e, self.__class__.__name__)