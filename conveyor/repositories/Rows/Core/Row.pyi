import typing
from ....core import Item as Item
from .Enums import Enums as Enums

class Row:
    type: Item.Type
    status: Item.Status
    digest: Item.Data.Digest
    metadata: Item.Metadata
    chain: str
    created: Item.Created
    reserver: Item.Reserver
    def metadata_valid(cls, metadata: Item.Metadata, values: dict[str, Item.Value | Item.Metadata.Value]) -> Item.Metadata: ...
    @classmethod
    def from_item(cls, item: Item) -> typing.Self: ...
    def dict_(self, enums: Enums.Enums, skip: set[str] = ...) -> dict[str, Item.Value]: ...
    def sub(self, another: Row, enums: Enums.Enums) -> dict[str, Item.Value]: ...
