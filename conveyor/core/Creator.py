import abc
import datetime
import pydantic

from . import Item, Chain, Data, Created



class Creator(metaclass=abc.ABCMeta):

	output_type: str
	output_status: str

	source_type: str | None = None
	source_status: str | None = None
	source_match: list[str] = []

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __init__(self, repository: Repository) -> None:
		self.repository = repository

	def create(self, *args, **kwargs) -> tuple[Data, Item.Metadata]:
		return Data(value=b''), Item.Metadata()

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def handleException(self, item: Item | None, e: Exception, worker: str) -> None:
		pass

	@pydantic.validate_arguments
	def handleNoException(self, item: Item) -> None:
		pass

	@property
	def name(self):
		return self.__class__.__name__

	def __call__(self, *args, **kwargs) -> None:

		try:

			data, metadata = self.create(*args, **kwargs)

			if self.source_type:

				try:
					chain = Chain(
						item=self.repository.get(
							type=self.source_type,
							where={
								key: metadata[key]
								for key in self.source_match
							} | (
								{'status': self.source_status}
								if self.source_status
								else {}
							)
						)[0]
					)

				except IndexError:
					chain = Chain(data=data)
			
			else:
				chain = Chain(data=data)

			item = Item(
				type=self.output_type,
				status=self.output_status,
				data=data,
				metadata=metadata,
				chain=chain,
				created=Created(datetime.datetime.utcnow()),
				reserved=None
			)

			self.repository.create(item)
			self.handleNoException(item)
		
		except Exception as e:
			self.handleException(None, e, self.__class__.__name__)