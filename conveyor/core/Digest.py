from __future__ import annotations

import base64
import typing
import pathlib
import pydantic



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Digest:

	value: pydantic.StrictBytes

	@pydantic.validator('value')
	def digest_length(cls, v):
		assert len(v) >= 32
		return v

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

	@classmethod
	@pydantic.validate_arguments
	def _group(cls, l: typing.Iterable[str], size: int) -> typing.Iterable:

		buffer = ''

		for e in l:
			if len(e) == 1:
				buffer += e
				if len(buffer) == size:
					yield buffer
					buffer = ''
			else:
				yield e

	@property
	def path(self) -> pathlib.Path:
		return pathlib.Path(
			*Digest._group(
				map(
					Digest._segment,
					self.string
				),
				1
			)
		)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __eq__(self, another) -> bool:
		return self.value == another.value