import os
import base64
import pathlib
import pydantic
from __future__ import annotations



@pydantic.dataclasses.dataclass(frozen=True)
class Digest:

	value: bytes

	@property
	def string(self) -> str:
		return base64.b64encode(
			self.value
		).decode('ascii')

	@classmethod
	@pydantic.validate_arguments
	def _segment(cls, s: str) -> str:
		if s == '+':
			return 'plus'
		elif s == '/':
			return 'slash'
		elif s == '=':
			return 'equal'
		else:
			return s

	@property
	def path(self) -> pathlib.Path:
		return pathlib.Path(
			*map(
				Digest._segment,
				self.string
			)
		)

	@pydantic.validate_arguments
	def __eq__(self, another: Digest) -> bool:
		return self.value == another.value