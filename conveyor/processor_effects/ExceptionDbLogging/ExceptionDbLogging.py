import pydantic
import dataclasses

from ...core import Effect, Item
from .ExceptionLogsRepository import ExceptionLogsRepository



@dataclasses.dataclass
class ExceptionDbLogging(Effect):

	logs_repository: ExceptionLogsRepository

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def handleException(self, item: Item, e: Exception, worker_name: str):
		self.logs_repository.create(item, e.__class__.__name__, str(e), worker_name)

	@pydantic.validate_arguments
	def handleNoException(self, item: Item, worker_name: str):
		self.logs_repository.delete(item, worker_name)