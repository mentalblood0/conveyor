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
	def value_or_string_valid(cls, value_or_string: pydantic.StrictBytes | Base64String) -> pydantic.StrictBytes | Base64String:

		match value_or_string:
			case bytes():
				value = value_or_string
			case Base64String():
				value = value_or_string.decoded
			case _ as unreachable:
				typing.assert_never(unreachable)

		if len(value) < 32:
			raise ValueError(f'`Digest` value must be of minimum length 32 (got {value} which is of length {len(value)})')

		return value_or_string

	@property
	def value(self) -> bytes:
		match self.value_or_string:
			case bytes():
				return self.value_or_string
			case Base64String():
				return self.value_or_string.decoded
			case _ as unreachable:
				typing.assert_never(unreachable)

	@property
	def string(self) -> str:
		match self.value_or_string:
			case Base64String():
				return self.value_or_string.value
			case bytes():
				return base64.b64encode(self.value_or_string).decode('ascii')
			case _ as unreachable:
				typing.assert_never(unreachable)

	@classmethod
	@pydantic.validate_arguments
	def _segment(cls, s: str) -> str:
		match s:
			case '+':
				return 'plus'
			case '/':
				return 'slash'
			case '=':
				return 'equal'
			case _:
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

	def __eq__(self, another: object) -> bool:
		match another:
			case Digest():
				return self.value == another.value
			case _:
				return False