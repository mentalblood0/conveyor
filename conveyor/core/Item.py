import typing
import datetime
import pydantic

from .Data import Data
from .Created import Created



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Item:

	Word          = pydantic.constr(min_length=1, regex=r'\w+', strict=True)
	# Word          = str
	BaseValue     = typing.Union[Word, 'Chain', Created]

	MetadataValue = pydantic.StrictStr | int | float | datetime.datetime
	Metadata      = dict[Word, MetadataValue]

	Value         = BaseValue | MetadataValue

	type: Word  # type: ignore
	status: Word  # type: ignore

	data: Data

	metadata: Metadata

	chain: 'Chain'
	created: Created
	reserved: str | None


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
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