import pydantic

from .ItemMask import ItemMask



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class ItemQuery:

	Limit = pydantic.PositiveInt
	Mask = ItemMask

	mask: ItemMask
	limit: Limit