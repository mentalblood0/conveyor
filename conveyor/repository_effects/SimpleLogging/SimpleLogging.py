import colorama
from logama import log

from ...core import Effect



class SimpleLogging(Effect):

	def create(self, item):
		log(f'-> {item.type}::{item.status} [{item.data_digest}]', colorama.Fore.GREEN)
	
	def update(self, item):
		log(f'{item.type}::?::{item.id} -> {item.type}::{item.status}', colorama.Fore.LIGHTBLUE_EX)

	def delete(self, type, id):
		log(f'{type}::?::{id} ->', colorama.Fore.LIGHTRED_EX)