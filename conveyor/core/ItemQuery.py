import pydantic

from .ItemMask import ItemMask



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class ItemQuery:

	Limit = int
	Mask = ItemMask

	mask: ItemMask
	limit: Limit

	@pydantic.validator('limit')
	def limit_valid(cls, limit: Limit) -> Limit:
		if limit <= 0:
			raise ValueError(f"Query result limit must be greater then 0 (received {limit} <= 0)")
		return limit