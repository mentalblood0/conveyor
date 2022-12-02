import pydantic

from .Data import Data
from .Chain import Chain
from .Created import Created



Metadata = dict[str, str | int | float]


@pydantic.dataclasses.dataclass(frozen=True)
class Item:

	type: str
	status: str

	data: Data

	metadata: Metadata

	chain: Chain
	created: Created
	reserved: str | None