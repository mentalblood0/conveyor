from ..Item import Item as Item

class Mask:
    type: Item.Type
    status: Item.Status | None
    data: Item.Data | None
    metadata: Item.Metadata | None
    chain: Item.Chain | None
    created: Item.Created | None
    reserver: Item.Reserver | None
