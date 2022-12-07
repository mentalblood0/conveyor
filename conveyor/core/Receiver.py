import abc
import uuid
import pydantic

from . import Item



class Receiver(metaclass=abc.ABCMeta):

	input_type: str
	input_status: str

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __init__(self, repository: Repository, limit: int = 256) -> None:

		self.repository = repository
		self.limit = limit

		self.id = uuid.uuid4().hex

	def reserve(self) -> None:
		self.repository.reserve(
			type=self.input_type,
			status=self.input_status,
			id=self.id,
			limit=self.limit
		)

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		self.repository.unreserve(item)

	def receive(self) -> list[Item]:

		self.reserve()

		return self.repository.get(
			self.input_type,
			where={'status': self.input_status},
			limit=self.limit,
			reserved=self.id
		)