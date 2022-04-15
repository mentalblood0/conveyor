import logging
import colorama
import dataclasses
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from ...core import Effect



def composeLogger(handler):

	logger = logging.getLogger(str(id(handler)))

	logger.propagate = False
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)

	return logger


@dataclasses.dataclass
class SimpleLogging(Effect):

	handler: StreamHandler | RotatingFileHandler = dataclasses.field(default_factory=StreamHandler)
	color: bool = True

	def __post_init__(self):

		self.handler.setFormatter(
			logging.Formatter(
				'%(asctime)s | %(message)s'
			)
		)

		self.logger = composeLogger(self.handler)

		print(self.handler, self.color)
		if self.color:
			self._withColor = lambda text, color: f'{color}{text}{colorama.Style.RESET_ALL}'
		else:
			self._withColor = lambda text, _: text

	def create(self, item):
		self.logger.info(self._withColor(f'CREATE | -> {item.type}::{item.status}', colorama.Fore.GREEN))

	def update(self, item):
		self.logger.info(self._withColor(f'UPDATE | {item.type}::?::{item.id} -> {item.type}::{item.status}', colorama.Fore.LIGHTBLUE_EX))

	def delete(self, type, id):
		self.logger.info(self._withColor(f'DELETE | {type}::?::{id} ->', colorama.Fore.LIGHTRED_EX))