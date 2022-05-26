import dataclasses

from ...core import Effect
from .ExceptionLogsRepository import ExceptionLogsRepository



@dataclasses.dataclass
class ExceptionDbLogging(Effect):

	logs_repository: ExceptionLogsRepository

	def handleException(self, item, e, worker_name):
		self.logs_repository.create(item, e.__class__.__name__, str(e), worker_name)