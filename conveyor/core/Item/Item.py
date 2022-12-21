import re
import types
import typing
import datetime
import pydantic

from .Data import Data
from .Chain import Chain
from .Created import Created
from .Reserver import Reserver



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Word:

	value: pydantic.StrictStr

	@pydantic.validator('value')
	def value_valid(cls, value: pydantic.StrictStr) -> pydantic.StrictStr:
		if re.match(r'\w+', value) is None:
			raise ValueError('`Word` value must be word')
		return value


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Item:

	@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
	class Metadata:

		Key = Word
		Value = pydantic.StrictStr | int | float | datetime.datetime | None

		value_: dict[Key, Value] | types.MappingProxyType

		@property
		def value(self) -> types.MappingProxyType:
			return types.MappingProxyType(self.value_)

	Type         = Word
	Status       = Word
	Data         = Data
	Chain        = Chain
	Created      = Created
	Reserver     = Reserver

	BaseKey      = Word
	Key          = BaseKey | Metadata.Key

	BaseValue    = typing.Union[Type, Status, Chain, Created, Reserver]
	Value        = BaseValue | Metadata.Value

	type:          Type
	status:        Status

	data:          Data

	metadata:      Metadata

	chain:         Chain
	created:       Created
	reserver:      Reserver

	def __eq__(self, another: 'Item') -> bool:
		return (
			self.type     == another.type and
			self.status   == another.status and
			self.data     == another.data and
			self.metadata == another.metadata and
			self.chain    == another.chain and
			self.created  == another.created
		)