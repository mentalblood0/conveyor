import typing
import datetime
import itertools
import sqlalchemy
import dataclasses

from ....core import Item, Transforms

from .Row import Row
from .Enums import Enums


BaseField = (
    typing.Literal["status"]
    | typing.Literal["digest"]
    | typing.Literal["chain"]
    | typing.Literal["created"]
    | typing.Literal["reserver"]
)


base_fields: tuple[
    typing.Literal["status"],
    typing.Literal["digest"],
    typing.Literal["chain"],
    typing.Literal["created"],
    typing.Literal["reserver"],
] = ("status", "digest", "chain", "created", "reserver")


Column = (
    sqlalchemy.Column[int]
    | sqlalchemy.Column[float]
    | sqlalchemy.Column[str]
    | sqlalchemy.Column[datetime.datetime]
)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Field:
    name: Item.Key
    value: Item.Value | Item.Data.Digest

    table: Item.Kind
    transform: Transforms.Safe[Item.Kind, str]

    enums: Enums.Enums

    @property
    def db_name(self) -> str:
        return self.column.name

    @property
    def db_table(self) -> str:
        return self.transform(self.table)

    @property
    def column(self):
        try:
            return next(iter(self.Column(self)))
        except StopIteration as e:
            raise ValueError(
                "Can not guess column type "
                f"corresponding to value with type `{type(self.value)}`"
            ) from e

    @dataclasses.dataclass(frozen=True, kw_only=False)
    class Column:
        source: "Field"

        def __iter__(self):
            return itertools.chain(
                self.enumerable,
                self.digest,
                self.chain,
                self.created,
                self.reserver,
                self.str_,
                self.int_,
                self.float_,
                self.datetime,
            )

        @property
        def enumerable(self):
            if isinstance(self.source.value, Item.Metadata.Enumerable):
                yield self.source.enums[(self.source.table, self.source.name)].column

        @property
        def digest(self):
            if isinstance(self.source.value, Item.Data.Digest):
                yield sqlalchemy.Column(
                    self.source.name.value, sqlalchemy.String(127), nullable=False
                )

        @property
        def chain(self):
            if isinstance(self.source.value, Item.Chain):
                yield sqlalchemy.Column(
                    self.source.name.value, sqlalchemy.String(127), nullable=False
                )

        @property
        def created(self):
            if isinstance(self.source.value, Item.Created):
                yield sqlalchemy.Column(
                    self.source.name.value,
                    sqlalchemy.DateTime(timezone=False),
                    nullable=False,
                )

        @property
        def reserver(self):
            if isinstance(self.source.value, Item.Reserver):
                yield sqlalchemy.Column(
                    self.source.name.value, sqlalchemy.String(31), nullable=True
                )

        @property
        def str_(self):
            if isinstance(self.source.value, str):
                yield sqlalchemy.Column(
                    self.source.name.value, sqlalchemy.String(255), nullable=True
                )

        @property
        def int_(self):
            if isinstance(self.source.value, int):
                yield sqlalchemy.Column(
                    self.source.name.value, sqlalchemy.Integer(), nullable=True
                )

        @property
        def float_(self):
            if isinstance(self.source.value, float):
                yield sqlalchemy.Column(
                    self.source.name.value, sqlalchemy.Float(), nullable=True
                )

        @property
        def datetime(self):
            if isinstance(self.source.value, datetime.datetime):
                yield sqlalchemy.Column(
                    self.source.name.value,
                    sqlalchemy.DateTime(timezone=False),
                    nullable=True,
                )

    def index(self, table: sqlalchemy.Table) -> sqlalchemy.Index:
        match self.value:
            case Item.Metadata.Enumerable():
                return self.enums[(self.table, self.name)].index(table)
            case _:
                return sqlalchemy.Index(
                    f"index__{self.name.value}", self.name.value, _table=table
                )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Fields:
    row: Row
    db: sqlalchemy.Engine

    table: Item.Kind
    transform: Transforms.Safe[Item.Kind, str]

    enums: Enums.Enums

    ignore = {"kind", "data", "metadata"}

    @property
    def fields(self) -> typing.Iterable[Field]:
        for k in {f.name for f in dataclasses.fields(self.row)} - self.ignore:
            yield Field(
                name=Item.Key(k),
                value=getattr(self.row, k),
                table=self.table,
                enums=self.enums,
                transform=self.transform,
            )

        for k in self.row.metadata:
            yield Field(
                name=Item.Key(k.value),
                value=self.row.metadata[k],
                table=self.table,
                enums=self.enums,
                transform=self.transform,
            )

    @property
    def columns(self) -> typing.Iterable[Column]:
        for f in self.fields:
            yield f.column
