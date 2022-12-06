import pydantic

from .Data import Data
from .Item import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
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