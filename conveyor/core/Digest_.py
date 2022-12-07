from __future__ import annotations

import base64
import typing
import pathlib
import pydantic



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Digest:

	init_value:     pydantic.StrictBytes | None = None
	init_string:    pydantic.StrictStr   | None = None

	@pydantic.validator('init_value')
	def init_value_correct(cls, init_value):
		if init_value is not None:
			if len(init_value) < 32:
				raise ValueError(f'`Digest` value must be of minimum length 32 (got {init_value} which is of length {len(init_value)})')
		return init_value

	@pydantic.validator('init_string')
	def init_string_correct(cls, init_string, values):

		if init_string is not None:
			Digest(
				init_value=base64.b64decode(
					init_string.encode('ascii')
				)
			)
		elif 'init_value' not in values:
			raise ValueError('`Digest`')

		return init_string

	@property
	def value(self) -> bytes:

		if self.init_value is not None:
			return self.init_value
		else:
			return base64.b64decode(
				self.init_string.encode('ascii')
			)

		raise ValueError

	@property
	def string(self) -> str:

		if type(self.value_or_string) is str:
			return self.value_or_string

		if type(self.value_or_string) is bytes:
			return base64.b64encode(
				self.value_or_string
			).decode('ascii')

		raise ValueError

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
	def _group(cls, l: typing.Iterable[str], size: int) -> typing.Iterable[str]:

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

	def __eq__(self, another) -> bool:
		return self.value == another.value