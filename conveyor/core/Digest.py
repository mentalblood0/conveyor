import base64
import typing
import pathlib
import pydantic



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Base64String:

	value: str

	@property
	def decoded(self):
		return base64.b64decode(
			self.value.encode('ascii')
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Digest:

	value_or_string: pydantic.StrictBytes | Base64String

	@pydantic.validator('value_or_string')
	def value_or_string_correct(cls, value_or_string):

		print('value_or_string', value_or_string)

		value: bytes | None = None

		if type(value_or_string) is bytes:
			value = value_or_string

		if type(value_or_string) is Base64String:
			value = value_or_string.decoded

		if value is None:
			raise ValueError

		if len(value) < 32:
			raise ValueError(f'`Digest` value must be of minimum length 32 (got {value} which is of length {len(value)})')

		return value_or_string

	@property
	def value(self) -> bytes:

		if type(self.value_or_string) is bytes:
			return self.value_or_string

		if type(self.value_or_string) is Base64String:
			return self.value_or_string.decoded

		raise ValueError

	@property
	def string(self) -> str:

		if type(self.value_or_string) is Base64String:
			return self.value_or_string.value

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