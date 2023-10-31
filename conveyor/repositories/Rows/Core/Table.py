import typing
import functools
import sqlalchemy
import dataclasses
import sqlalchemy.exc

from .Fields import Field


@dataclasses.dataclass(frozen=True, kw_only=True)
class Table:
    connection: sqlalchemy.Connection
    name: str
    fields: typing.Iterable[Field]

    @functools.cached_property
    def _fields(self):
        return (*self.fields,)

    @functools.cached_property
    def table(self):
        return sqlalchemy.Table(
            self.name, sqlalchemy.MetaData(), *(f.column for f in self._fields)
        )

    @functools.cached_property
    def current_columns(self):
        return {
            c["name"]
            for c in sqlalchemy.inspect(self.connection).get_columns(self.name)
        }

    def alter(self):
        for f in self._fields:
            if f.db_name not in self.current_columns:
                self.connection.execute(
                    sqlalchemy.sql.text(
                        f"ALTER TABLE {self.name} "
                        f"ADD COLUMN {f.column.name} {f.column.type}"
                    )
                )
                if not (i := f.index(self.table)) in self.table.indexes:
                    i.create(bind=self.connection)

    def create(self):
        table = sqlalchemy.Table(
            self.name, sqlalchemy.MetaData(), *(f.column for f in self._fields)
        )
        table.create(bind=self.connection)

        for i in table.indexes - {f.index(table) for f in self._fields}:
            i.create(bind=self.connection)

    def __post_init__(self):
        try:
            self.alter()
        except sqlalchemy.exc.NoSuchTableError:
            self.create()
