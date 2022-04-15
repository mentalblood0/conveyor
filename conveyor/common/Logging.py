import logging
import colorama
import dataclasses
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from ..core import Effect



def composeLogger(handler):

	logger = logging.getLogger(str(id(handler)))

	logger.propagate = False
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)

	return logger


@dataclasses.dataclass
class Logging(Effect):

	handler: StreamHandler | RotatingFileHandler = dataclasses.field(default_factory=StreamHandler)
	color: bool = True

	def __post_init__(self):

		self.handler.setFormatter(
			logging.Formatter(
				'%(asctime)s | %(message)s'
			)
		)

		self.logger = composeLogger(self.handler)

		if self.color:
			self._withColor = lambda text, color: f'{color}{text}{colorama.Style.RESET_ALL}'
		else:
			self._withColor = lambda text, _: text