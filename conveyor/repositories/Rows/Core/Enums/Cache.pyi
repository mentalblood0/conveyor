from .....core import Item as Item
from ..Connect import Connect as Connect
from .Columns import columns as columns

class TableCache:
    value: dict[Item.Metadata.Enumerable, int]
    description: dict[int, Item.Metadata.Enumerable]

class Cache(dict[str, TableCache]):
    TableCache = TableCache
    def load(self, table: str, connect: Connect): ...
