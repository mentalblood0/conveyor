import types
import typing
import pydantic
import datetime

from .Word import Word
from .Enumerable import Enumerable



@pydantic.dataclasses.dataclass(frozen = True, kw_only = False, config = {'arbitrary_types_allowed': True})
class Metadata:

	class Key(Word): pass
	Value = pydantic.StrictStr | int | float | datetime.datetime | Enumerable | None

	Enumerable = Enumerable

	value_: dict[Key, Value] | types.MappingProxyType[Key, Value]

	@property
	def value(self) -> types.MappingProxyType[Key, Value]:
		return types.MappingProxyType(self.value_)

	@pydantic.validate_arguments
	def __getitem__(self, key: str | Key) -> Value:
		match key:
			case Metadata.Key():
				return self.value[key]
			case str():
				return self[Metadata.Key(key)]

	def __or__(self, o: typing.Any) -> typing.Self:
		match o:
			case dict():
				return Metadata(self.value | o)
			case Metadata():
				return self | o.value
			case _:
				raise ValueError(f'Metadata instance can be joined only with another Metadata instance or dictionary (got {type(o)})')

	def __ror__(self, __value: typing.Any) -> typing.Self:
		return self | __value

	def keys(self):
		return self.value.keys()

	def values(self):
		return self.value.values()

	def items(self):
		return self.value.items()

	def __iter__(self):
		return self.value.__iter__()