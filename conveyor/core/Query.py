import pydantic

from .Mask import Mask



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Query:

	Limit = pydantic.PositiveInt
	Mask = Mask

	mask: Mask
	limit: Limit