import dataclasses

from .Mask import Mask


@dataclasses.dataclass(frozen=True, kw_only=True)
class Query:
    Mask = Mask
    Limit = int | None

    mask: Mask
    limit: Limit
