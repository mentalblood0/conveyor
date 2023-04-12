import sqlalchemy
import typing
from ....core import Item as Item, Transforms as Transforms
from .Enums import Enums as Enums
from .Row import Row as Row
from _typeshed import Incomplete

BaseField: Incomplete
base_fields: tuple[typing.Literal['status'], typing.Literal['digest'], typing.Literal['chain'], typing.Literal['created'], typing.Literal['reserver']]
Column: Incomplete

class Field:
    name: Item.Key
    value: Item.Value | Item.Data.Digest
    table: Item.Type
    transform: Transforms.Safe[Item.Type, str]
    enums: Enums.Enums
    @property
    def db_name(self) -> str: ...
    @property
    def db_table(self) -> str: ...
    @property
    def column(self) -> Column: ...
    def index(self, table: sqlalchemy.Table) -> sqlalchemy.Index: ...

class Fields:
    row: Row
    db: sqlalchemy.Engine
    table: Item.Type
    transform: Transforms.Safe[Item.Type, str]
    enums: Enums.Enums
    ignore: Incomplete
    @property
    def fields(self) -> typing.Iterable[Field]: ...
    @property
    def columns(self) -> typing.Iterable[Column]: ...
