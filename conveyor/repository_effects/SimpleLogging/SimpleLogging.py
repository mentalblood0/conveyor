import sys
import colorama
from io import IOBase
from logama import log
from dataclasses import dataclass

from ...core import Effect



@dataclass
class SimpleLogging(Effect):

	file: IOBase = sys.stderr
	color: bool = True

	def __post_init__(self):
		if self.color:
			self.colors = {
				'create': colorama.Fore.GREEN,
				'update': colorama.Fore.LIGHTBLUE_EX,
				'delete': colorama.Fore.LIGHTRED_EX
			}
		else:
			self.colors = {
				'create': '',
				'update': '',
				'delete': ''
			}

	def create(self, item):
		log(f'-> {item.type}::{item.status} [{item.data_digest}]', self.colors['create'], self.file)
	
	def update(self, item):
		log(f'{item.type}::?::{item.id} -> {item.type}::{item.status}', self.colors['update'], self.file)

	def delete(self, type, id):
		log(f'{type}::?::{id} ->', self.colors['delete'], self.file)