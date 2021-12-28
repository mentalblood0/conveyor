from __future__ import annotations

from functools import partial
from abc import ABCMeta, abstractmethod

from . import Item



class Command(metaclass=ABCMeta):

	@abstractmethod
	def __call__(self, *args, **kwargs):
		pass

	@abstractmethod
	def revert(self, *args, **kwargs):
		pass


class Transaction:

	def __init__(self, commands: dict[str, Command]=None, sequence: list[Command]=None):

		self.commands = commands or {}
		self.sequence = sequence or []
	
	def __getattribute__(self, name: str) -> callable:
		
		if (not name in ['execute']) and (name in self.commands):

			return lambda *args, **kwargs: Transaction(
				commands=self.commands,
				sequence=self.sequence + [partial(self.commands[name], *args, **kwargs)]
			)
		
		raise AttributeError(object=self, name=name)

	def execute(self) -> int:
		
		for i, c in enumerate(self.sequence):

			try:
				c()
			
			except Exception as e:
				
				for executed in self.sequence[:i]:
					executed.revert()
				
				raise e
				return i
		
		return len(self.sequence)


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