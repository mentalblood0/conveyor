from __future__ import annotations

from functools import partial

from . import Command



class Transaction:

	def __init__(self, commands: dict[str, Command]=None, sequence: list[Command]=None):

		self.commands = commands or {}
		self.sequence = sequence or []
	
	def __getattribute__(self, name: str) -> Transaction:
		
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