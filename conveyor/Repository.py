from abc import ABCMeta
from copy import deepcopy
from functools import partial

from .Command import Command
from .Transaction import Transaction



class Repository(metaclass=ABCMeta):

	commands: dict[str, Command]
	queries: dict[str, callable]

	def __init__(self, *args, **kwargs):

		self.commands = {
			k: partial(deepcopy(v)(), *args, **kwargs)
			for k, v in self.commands.items()
		}

		self.queries = {
			k: partial(deepcopy(v), *args, **kwargs)
			for k, v in self.queries.items()
		}
	
	def __getattribute__(self, name: str):
		
		if name in ['transaction', 'queries', 'commands']:
			return super().__getattribute__(name)
		
		return self.queries[name]
	
	def transaction(self):
		return Transaction(self.commands, [])