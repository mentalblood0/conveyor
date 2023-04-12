import sqlalchemy.exc
import typing
from .Fields import Field as Field

def Table(connection: sqlalchemy.Connection, name: str, fields: typing.Iterable[Field]) -> None: ...
