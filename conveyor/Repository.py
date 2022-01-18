from __future__ import annotations

from abc import ABCMeta
from copy import deepcopy
from functools import partial

from .Command import Command
from .Transaction import Transaction



class Repository(metaclass=ABCMeta):

	subrepositories: dict[str, Repository]

	commands: dict[str, Command]
	queries: dict[str, callable]

	def __init__(self, *args, **kwargs):

		kwargs['r'] = self

		self.commands = {
			k: partial(deepcopy(v)(), *args, **kwargs)
			for k, v in self.commands.items()
		}

		self.queries = {
			k: partial(deepcopy(v), *args, **kwargs)
			for k, v in self.queries.items()
		}

		for R_name, R in self.subrepositories.items():

			r = R(*args, **kwargs)
			
			for name, c in r.commands.items():
				self.commands[f'{R_name}_{name}'] = c
			
			for name, q in r.queries.items():
				self.queries[f'{R_name}_{name}'] = q
	
	def __getattribute__(self, name: str):
		
		if name in ['transaction', 'queries', 'commands', 'subrepositories']:
			return super().__getattribute__(name)
		
		return self.queries[name]
	
	def transaction(self):
		return Transaction(self.commands, [])