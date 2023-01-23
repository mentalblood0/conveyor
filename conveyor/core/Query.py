import pydantic

from .Mask import Mask



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Query:

	Limit = pydantic.PositiveInt | None
	Mask = Mask

	mask: Mask
	limit: Limit