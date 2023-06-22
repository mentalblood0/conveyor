import base64
import pydantic



@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class Base64String:

	value: str

	@property
	def decoded(self):
		return base64.b64decode(
			self.value.encode('ascii')
		)


@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class Digest:

	Base64String = Base64String

	value_or_string: pydantic.StrictBytes | Base64String

	@pydantic.validator('value_or_string')
	def value_or_string_valid(cls, value_or_string: pydantic.StrictBytes | Base64String) -> pydantic.StrictBytes | Base64String:

		match value_or_string:
			case bytes():
				value = value_or_string
			case Base64String():
				value = value_or_string.decoded

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

	@property
	def string(self) -> str:
		match self.value_or_string:
			case Base64String():
				return self.value_or_string.value
			case bytes():
				return base64.b64encode(self.value_or_string).decode('ascii')

	def __eq__(self, another: object) -> bool:
		match another:
			case Digest():
				return self.value == another.value
			case _:
				raise ValueError(f'Can not compare instance of type `Digest` with instance of type `{type(another)}`')