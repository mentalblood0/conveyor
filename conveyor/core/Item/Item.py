import re
import types
import typing
import datetime
import pydantic

from .Data import Data
from .Created import Created
from .Reserver import Reserver



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Word:

	value: pydantic.StrictStr

	@pydantic.validator('value')
	def value_correct(cls, value):
		if re.match(r'\w+', value) is None:
			raise ValueError('`Word` value must be word')
		return value


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Item:

	@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
	class Metadata:

		Key = Word
		Value = pydantic.StrictStr | int | float | datetime.datetime | None

		value: dict[Key, Value]

		@pydantic.validator('value')
		def value_correct(cls, value):
			return types.MappingProxyType(value)

	Type         = Word
	Status       = Word
	Data         = Data
	Created      = Created
	Reserver     = Reserver

	BaseKey      = Word
	Key          = BaseKey | Metadata.Key

	BaseValue    = typing.Union[Type, Status, 'Chain', Created, Reserver]
	Value        = BaseValue | Metadata.Value

	type:          Type
	status:        Status

	data:          Data

	metadata:      Metadata

	chain:         'Chain'
	created:       Created
	reserver:      Reserver



from ..Chain import Chain
getattr(Item, '__pydantic_model__').update_forward_refs()