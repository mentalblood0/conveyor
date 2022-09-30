import pydantic
import colorama
import dataclasses

from ...core import Item
from ...common import Logging



@dataclasses.dataclass
class SimpleLogging(Logging):

	@pydantic.validate_arguments
	def create(self, item: Item, ref: Item = None):
		self.logger.info(self._withColor(f'CREATE | -> {item.type}::{item.status}', colorama.Fore.GREEN))

	@pydantic.validate_arguments
	def update(self, item: Item):
		self.logger.info(self._withColor(f'UPDATE | {item.type}::?::{item.id} -> {item.type}::{item.status}', colorama.Fore.LIGHTBLUE_EX))

	@pydantic.validate_arguments
	def delete(self, type: str, id: str | int):
		self.logger.info(self._withColor(f'DELETE | {type}::?::{id} ->', colorama.Fore.LIGHTRED_EX))