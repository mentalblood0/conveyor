from functools import partial
from abc import ABCMeta, abstractmethod

from . import Item, Command, Transaction



class ItemRepository(metaclass=ABCMeta):

	commands: dict[str, Command]

	def __init__(self, *args, **kwargs):
		for k, v in self.commands.items():
			self.commands[k] = partial(v, *args, **kwargs)
	
	def transaction(self):
		return Transaction(self.commands, [])
	
	@abstractmethod
	def get(self, type: str, status: str, limit: int=None) -> Item:
		pass