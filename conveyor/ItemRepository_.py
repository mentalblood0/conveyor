from abc import ABCMeta
from functools import partial

from . import Command, Transaction



class ItemRepository(metaclass=ABCMeta):

	commands: dict[str, Command]
	queries: dict[str, callable]

	def __init__(self, *args, **kwargs):

		for k, v in self.commands.items():
			self.commands[k] = partial(v, *args, **kwargs)
		
		for k, v in self.queries.items():
			self.queries[k] = partial(v, *args, **kwargs)
	
	def __getattribute__(self, name: str):
		
		if name in ['transaction']:
			return super().__getattribute__(name)
		
		return self.queries[name]
	
	def transaction(self):
		return Transaction(self.commands, [])