import datetime
import pydantic
import dataclasses

from .Data import Data
from .Created import Created



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Chain:

	ref: Data
	value: str = dataclasses.field(init=False, default='')

	@pydantic.validator('value')
	def value_correct(cls, value, values):
		if 'ref' in values:
			return values['ref'].digest.string


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Item:

	Word          = pydantic.constr(min_length=1, regex=r'\w+', strict=True)
	# Word          = str
	BaseValue     = Word | Chain | Created

	MetadataValue = pydantic.StrictStr | int | float | datetime.datetime
	Metadata      = dict[Word, MetadataValue]

	Value         = BaseValue | MetadataValue

	type: Word  # type: ignore
	status: Word  # type: ignore

	data: Data

	metadata: Metadata

	chain: Chain
	created: Created
	reserved: str | None
