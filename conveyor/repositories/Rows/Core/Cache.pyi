from . import Enums as Enums
from _typeshed import Incomplete

class Cache(dict[str, Enums.Cache]):
    def __getitem__(self, __key: str) -> Enums.Cache: ...

cache: Incomplete
