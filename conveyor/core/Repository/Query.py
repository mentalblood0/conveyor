import pydantic

from .Mask import Mask



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Query:

	Mask  = Mask
	Limit = pydantic.PositiveInt | None

	mask  : Mask
	limit : Limit