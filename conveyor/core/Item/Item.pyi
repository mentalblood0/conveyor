import pydantic
import types
from .Chain import Chain as Chain
from .Created import Created as Created
from .Data import Data as Data
from .Reserver import Reserver as Reserver
from _typeshed import Incomplete

class Enumerable:
    value: pydantic.StrictStr | None

class Word(Enumerable):
    value: pydantic.StrictStr
    def value_valid(cls, value: pydantic.StrictStr) -> pydantic.StrictStr: ...

class ItemKey(Word): ...

class Metadata:
    class Key(Word): ...
    Value: Incomplete
    Enumerable = Enumerable
    value_: dict[Key, Value] | types.MappingProxyType[Key, Value]
    @property
    def value(self) -> types.MappingProxyType[Key, Value]: ...

class Item:
    class Type(Word): ...
    class Status(Word): ...
    Data = Data
    Chain = Chain
    Created = Created
    Reserver = Reserver
    Metadata = Metadata
    Key = ItemKey
    BaseValue: Incomplete
    Value: Incomplete
    type: Type
    status: Status
    data: Data
    metadata: Metadata
    chain: Chain
    created: Created
    reserver: Reserver
