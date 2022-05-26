import colorama
import traceback

from ...common import Logging



class ExceptionLogging(Logging):

	def handleException(self, item, e, worker_name):
		text = ''.join(traceback.format_exception(e)[1:])
		self.logger.error(self._withColor(f'{worker_name}({item.type}::{item.status}::{item.id}):\n{text}', colorama.Fore.RED))