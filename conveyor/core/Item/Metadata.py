import types
import typing
import datetime
import dataclasses

from .Word import Word
from .Enumerable import Enumerable



@dataclasses.dataclass(frozen = True, kw_only = False)
class Metadata:

	class Key(Word): pass
	Value = str | int | float | datetime.datetime | Enumerable | None

	Enumerable = Enumerable

	value_: dict[Key, Value] | types.MappingProxyType[Key, Value]

	@property
	def value(self) -> types.MappingProxyType[Key, Value]:
		return types.MappingProxyType(self.value_)

	def __getitem__(self, key: str | Key) -> Value:
		match key:
			case Metadata.Key():
				return self.value[key]
			case str():
				return self[Metadata.Key(key)]

	def __or__(self, o: dict[Key, Value] | typing.Mapping[Key, Value] | 'Metadata') -> typing.Self:
		match o:
			case dict() | typing.Mapping():
				return Metadata(self.value | o)
			case Metadata():
				return self | o.value
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