import pydantic
import dataclasses

from .Item import Item
from .Data import Data



@pydantic.dataclasses.dataclass(frozen=True)
class Chain:

	value: str = dataclasses.field(init=False)

	data: dataclasses.InitVar[Data | None] = None
	item: dataclasses.InitVar[Item | None] = None

	def __post_init__(self, data, item):

		if data is not None:
			object.__setattr__(self, 'value', data.digest.string)

		if item is not None:
			object.__setattr__(self, 'value', item.chain.value)