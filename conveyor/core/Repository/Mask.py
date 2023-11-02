import dataclasses

from ..Item import Item


@dataclasses.dataclass(frozen=True, kw_only=True)
class Mask:
    kind: Item.Kind
    status: Item.Status | None = None
    data: Item.Data | None = None
    metadata: Item.Metadata | None = None
    chain: Item.Chain | None = None
    created: Item.Created | None = None
    reserver: Item.Reserver | None = None
