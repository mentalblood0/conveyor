import colorama
import traceback

from ...common import Logging



class ExceptionLogging(Logging):

	def handleException(self, e):
		text = ''.join(traceback.format_exception(e)[1:])
		self.logger.error(self._withColor(f'{self.__class__.__name__}:\n{text}', colorama.Fore.RED))