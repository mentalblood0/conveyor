import colorama
import traceback

from ...common import Logging



class ExceptionLogging(Logging):

	def handleException(self, e, name):
		text = ''.join(traceback.format_exception(e)[1:])
		self.logger.error(self._withColor(f'{name}:\n{text}', colorama.Fore.RED))