import colorama
from logama import log

from ... import RepositoryEffect



class SimpleLogging(RepositoryEffect):

	def create(self, item):
		log(f'-> {item.type}::{item.status}', colorama.Fore.GREEN)
	
	def update(self, type, id, item):
		log(f'{type}::?::{id} -> {type}::{item.status}', colorama.Fore.LIGHTBLUE_EX)

	def delete(self, type, id):
		log(f'{type}::?::{id} ->', colorama.Fore.LIGHTRED_EX)