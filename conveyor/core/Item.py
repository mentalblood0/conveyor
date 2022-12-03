import datetime
import pydantic

from .Data import Data
from .Chain import Chain
from .Created import Created



@pydantic.dataclasses.dataclass(frozen=True)
class Item:

	BaseValue = str | datetime.datetime
	MetadataValue = str | int | float | datetime.datetime
	Value = BaseValue | MetadataValue

	Metadata = dict[str, MetadataValue]

	type: str
	status: str

	data: Data

	metadata: Metadata

	chain: Chain
	created: Created
	reserved: str | None