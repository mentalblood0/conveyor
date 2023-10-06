import base64
import dataclasses



@dataclasses.dataclass(frozen = True, kw_only = False)
class Base64String:

	value: str

	@property
	def decoded(self):
		return base64.b64decode(
			self.value.encode('ascii')
		)


@dataclasses.dataclass(frozen = True, kw_only = False)
class Digest:

	Base64String = Base64String

	value_or_string: bytes | Base64String

	def __post_init__(self):
		if (given := len(self.value)) < (required := 32):
			raise ValueError(f'`Digest` value must be of minimum length {required} (got {self.value} which is of length {given})')

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