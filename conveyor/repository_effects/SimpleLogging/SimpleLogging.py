import colorama
import dataclasses

from ...common import Logging



@dataclasses.dataclass
class SimpleLogging(Logging):

	def create(self, item):
		self.logger.info(self._withColor(f'CREATE | -> {item.type}::{item.status}', colorama.Fore.GREEN))

	def update(self, item):
		self.logger.info(self._withColor(f'UPDATE | {item.type}::?::{item.id} -> {item.type}::{item.status}', colorama.Fore.LIGHTBLUE_EX))

	def delete(self, type, id):
		self.logger.info(self._withColor(f'DELETE | {type}::?::{id} ->', colorama.Fore.LIGHTRED_EX))