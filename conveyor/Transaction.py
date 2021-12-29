from __future__ import annotations

from typing import Union
from functools import partial

from . import Command



class Transaction:

	def __init__(self, commands: dict[str, Command]=None, sequence: list[Command]=None):

		self.commands = commands or {}
		self.sequence = sequence or []
	
	def append(self, name: str, *args, **kwargs):

		self.sequence.append(partial(self.commands[name], *args, **kwargs))

		return self
	
	def __getattribute__(self, name: str):

		if name in ['execute', 'append', 'sequence', 'commands']:
			return super().__getattribute__(name)

		return lambda *args, **kwargs: self.append(name, *args, **kwargs)

	def execute(self) -> int:
		
		for i, c in enumerate(self.sequence):

			try:
				c()
			
			except Exception as e:
				
				for executed in self.sequence[:i+1]:
					executed.func.revert()
				
				raise e
				return i
		
		return len(self.sequence)