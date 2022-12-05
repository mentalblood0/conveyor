import re
import typing
import datetime
import pydantic
import frozendict

from .Data import Data
from .Created import Created



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Word:

	value: pydantic.StrictStr

	@pydantic.validator('value')
	def value_correct(cls, value):
		if re.match(r'\w+', value) is None:
			raise ValueError('`Word` value must be word')
		return value


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Item:

	@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
	class Metadata:

		Value = pydantic.StrictStr | int | float | datetime.datetime

		value: dict[Word, Value]

		@pydantic.validator('value')
		def value_correct(cls, value):
			return frozendict.frozendict(value)

	BaseValue     = typing.Union[Word, 'Chain', Created]
	Value         = BaseValue | Metadata.Value

	type: Word
	status: Word

	data: Data

	metadata: Metadata

	chain: 'Chain'
	created: Created
	reserved: str | None


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Chain:

	ref: Data | Item

	@property
	def value(self) -> str:

		if type(self.ref) is Data:
			return self.ref.digest.string

		if type(self.ref) is Item:
			return self.ref.chain.value

		raise ValueError

	def __eq__(self, another: 'Chain') -> bool:
		return self.value == another.value


Item.__pydantic_model__.update_forward_refs()