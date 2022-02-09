import colorama
from datetime import datetime

from .. import RepositoryEffect



class SimpleLogging(RepositoryEffect):

	def __init__(self):
		colorama.init()
	
	def _log(self, message, style):
		print(f"{datetime.now()} | {style}{message}{colorama.Style.RESET_ALL}")

	def create(self, item):
		self._log(f'-> {item.type}::{item.status}', colorama.Fore.GREEN)
	
	def update(self, type, id, item):
		self._log(f'{type}::?::{id} -> {type}::{item.status}', colorama.Fore.LIGHTBLUE_EX)

	def delete(self, type, id):
		self._log(f'{type}::?::{id} ->', colorama.Fore.RED)

colorama.Fore.