import typing
import dataclasses

from .Word import Word
from .Data import Data
from .Chain import Chain
from .Created import Created
from .Reserver import Reserver
from .Metadata import Metadata


@dataclasses.dataclass(frozen=True, kw_only=True)
class Item:
    class Type(Word):
        pass

    class Status(Word):
        pass

    Data = Data
    Chain = Chain
    Created = Created
    Reserver = Reserver
    Metadata = Metadata

    class Key(Word):
        pass

    BaseValue = typing.Union[Data, Type, Status, Chain, Created, Reserver]
    Value = BaseValue | Metadata.Value

    type: Type
    status: Status

    data: Data

    metadata: Metadata

    chain: Chain
    created: Created
    reserver: Reserver = dataclasses.field(compare=False)
