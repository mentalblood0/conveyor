import datetime
import pydantic
import dataclasses

from .Data import Data
from .Created import Created



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Item:

	BaseValue = str | datetime.datetime
	MetadataValue = str | int | float | datetime.datetime
	Value = BaseValue | MetadataValue

	Metadata = dict[str, MetadataValue]

	type: str
	status: str

	data: Data

	metadata: Metadata

	chain: 'Chain'
	created: Created
	reserved: str | None


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Chain:

	value: str = dataclasses.field(init=False)

	data: dataclasses.InitVar[Data | None] = None
	item: dataclasses.InitVar[Item | None] = None

	def __post_init__(self, data, item):

		if data is not None:
			object.__setattr__(self, 'value', data.digest.string)

		if item is not None:
			object.__setattr__(self, 'value', item.chain.value)