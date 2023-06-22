import re
import types
import typing
import datetime
import pydantic
import dataclasses

from .Data import Data
from .Chain import Chain
from .Created import Created
from .Reserver import Reserver



@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class Enumerable:
	value: pydantic.StrictStr | None


@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class Word(Enumerable):

	value: pydantic.StrictStr

	@pydantic.validator('value')
	def value_valid(cls, value: pydantic.StrictStr) -> pydantic.StrictStr:
		if re.match(r'\w+', value) is None:
			raise ValueError('`Word` value must be word')
		return value


class ItemKey(Word): pass


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


@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Item:

	class Type(Word)   : pass
	class Status(Word) : pass
	Data      = Data
	Chain     = Chain
	Created   = Created
	Reserver  = Reserver
	Metadata  = Metadata

	Key       = ItemKey

	BaseValue = typing.Union[Data, Type, Status, Chain, Created, Reserver]
	Value     = BaseValue | Metadata.Value

	type      : Type
	status    : Status

	data      : Data

	metadata  : Metadata

	chain     : Chain
	created   : Created
	reserver  : Reserver = dataclasses.field(compare=False)