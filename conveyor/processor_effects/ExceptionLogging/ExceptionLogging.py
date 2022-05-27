import colorama
import pydantic
import traceback

from ...core import Item
from ...common import Logging



class ExceptionLogging(Logging):

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def handleException(self, item: Item, e: Exception, worker_name: str):
		text = ''.join(traceback.format_exception(e)[1:])
		self.logger.error(self._withColor(f'{worker_name}({item.type}::{item.status}::{item.id}):\n{text}', colorama.Fore.RED))