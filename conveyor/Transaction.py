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

		print('start executing', [e.func for e in self.sequence])

		result = []

		for i, c in enumerate(self.sequence):

			try:
				print('execute', c.func)
				result.append(c())
				print('result:', result[-1])
			
			except Exception as e:
				
				for executed in reversed(self.sequence[:i+1]):
					print('revert', executed.func)
					executed.func.revert()
				
				print('end executing', [e.func for e in self.sequence])
				raise e
		
		print('end executing', [e.func for e in self.sequence])
		return result
	
	def __repr__(self) -> str:

		return str([
			(e.func.__class__.__name__, e.func.args, e.func.kwargs)
			for e in self.sequence
		])