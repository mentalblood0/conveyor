from __future__ import annotations

import typing
import datetime
import functools
import itertools
import contextlib
import sqlalchemy
import dataclasses
import sqlalchemy.exc

from .Enums import Enums

from ....core import Item, Query, Transforms

from . import Cache
from .Row import Row
from . import Fields
from .Table import Table
from .DbEnumName import DbEnumName
from .DbTableName import DbTableName


@dataclasses.dataclass(frozen=True, kw_only=False)
class Core:
    Item = Row

    db: sqlalchemy.engine.Engine
    connection: sqlalchemy.Connection | None = None

    table: Transforms.Safe[Item.Kind, str] = DbTableName("conveyor")
    enum: Transforms.Safe[Item.Key, str] = DbEnumName("enum")

    @property
    def _cache_id(self) -> str:
        return str(self.db)

    @property
    def _cache(self) -> Cache.Enums.Cache:
        return Cache.cache[self._cache_id]

    @property
    def _enums(self) -> Enums.Enums:
        return Enums.Enums(
            connect=self._connect,
            kind_transform=self.table,
            enum_transform=self.enum,
            cache_id=self._cache_id,
        )

    @dataclasses.dataclass(frozen=True, kw_only=True)
    class Where:
        ref: Row | Query.Mask
        rows: Core

        def __iter__(self):
            return itertools.chain(
                self.status, self.chain, self.created, self.reserver, self.metadata
            )

        @property
        def status(self):
            if self.ref.status is not None:
                yield self.rows._enums[(self.ref.kind, Item.Key("status"))].eq(
                    self.ref.status
                )

        @property
        def chain(self):
            match self.ref.chain:
                case None:
                    """"""
                case str():
                    yield sqlalchemy.column("chain") == self.ref.chain
                case _:
                    yield sqlalchemy.column("chain") == self.ref.chain.value

        @property
        def created(self):
            if self.ref.created is not None:
                yield sqlalchemy.column("created") == self.ref.created.value

        @property
        def reserver(self):
            if self.ref.reserver is not None:
                yield sqlalchemy.column("reserver") == self.ref.reserver.value

        @property
        def metadata(self):
            if self.ref.metadata is not None:
                for k, v in self.ref.metadata.items():
                    match v:
                        case Item.Metadata.Enumerable():
                            yield self.rows._enums[
                                (self.ref.kind, Item.Key(k.value))
                            ].eq(v)
                        case _:
                            yield sqlalchemy.column(k.value) == v

    def _where_string(self, ref: Row | Query.Mask) -> str:
        return " and ".join(
            str(c.compile(bind=self.db, compile_kwargs={"literal_binds": True}))
            for c in self.Where(ref=ref, rows=self)
        )

    def _compile(self, v: Item.Value) -> str:
        return str(
            sqlalchemy.text(":v")
            .bindparams(v=v)
            .compile(bind=self.db, compile_kwargs={"literal_binds": True})
        )

    def _values(self, d: dict[str, Item.Value]) -> str:
        keys = ", ".join(d)
        values = ", ".join(self._compile(v) for v in d.values())
        return f"({keys}) values ({values})"

    def _set(self, d: dict[str, Item.Value]) -> str:
        return ", ".join(f"{k} = {self._compile(v)}" for k, v in d.items())

    def append(self, row: Row) -> None:
        name = self.table(row.kind)

        created = False
        for _ in range(5):
            try:
                with self._connect() as connection:
                    connection.execute(
                        sqlalchemy.text(
                            f"insert into {name} "
                            f"{self._values(row.Dict(row=row, enums=self._enums)())}"
                        )
                    )
                break
            except Exception:
                if not created:
                    with self._connect() as connection:
                        Table(
                            connection=connection,
                            name=name,
                            fields=Fields.Fields(
                                row=row,
                                db=self.db,
                                table=row.kind,
                                transform=self.table,
                                enums=self._enums,
                            ).fields,
                        )
                created = True

    @dataclasses.dataclass(frozen=True, kw_only=True)
    class Get:
        rows: Core
        query: Query

        def __str__(self):
            q = f"select * from {self.rows.table(self.query.mask.kind)}"
            if where := self.rows._where_string(self.query.mask):
                q = f"{q} where {where}"
            if self.query.limit is not None:
                q = f"{q} limit {self.query.limit}"
            return q

        @functools.cached_property
        def raw(self):
            with self.rows._connect() as connection:
                return (*connection.execute(sqlalchemy.text(str(self))),)

        def status_enum(self, r: sqlalchemy.Row[typing.Any]):
            return self.rows._enums[(self.query.mask.kind, Item.Key("status"))]

        def status(self, r: sqlalchemy.Row[typing.Any]):
            enum = self.status_enum(r)
            if (result := enum.string(getattr(r, enum.db_field)).value) is None:
                raise TypeError("Status value can not be None")
            return Item.Status(result)

        @dataclasses.dataclass(frozen=True, kw_only=True)
        class Metadata:
            source: Core.Get
            row: sqlalchemy.Row[typing.Any]

            def _base_field(self, name: str):
                return name in (f.name for f in dataclasses.fields(Item))

            def _base_inner_field(self, name: str):
                return name in ("digest", self.source.status_enum(self.row).db_field)

            def _key(self, name: str):
                return not (self._base_field(name) or self._base_inner_field(name))

            @functools.cached_property
            def _names(self):
                return (
                    name
                    for name in self.row.__getstate__()["_parent"].__getstate__()[
                        "_keys"
                    ]
                    if self._key(name)
                )

            def _enum(self, name: str):
                if not isinstance(value := getattr(self.row, name), int | None):
                    raise TypeError(
                        f"Expected column `{name}` "
                        f"in table `{self.source.query.mask.kind.value}` "
                        "to hold enumerable using integer or null value"
                    )
                unenumed = (~self.source.rows.enum)(name)
                enum_id = (self.source.query.mask.kind, unenumed)
                return Item.Metadata.Key(unenumed.value), self.source.rows._enums[
                    enum_id
                ].convert(value)

            def _not_enum(self, name: str):
                return Item.Metadata.Key(name), getattr(self.row, name)

            def __call__(self):
                result: Item.Metadata.Mutable = {}
                for name in self._names:
                    if (~self.source.rows.enum).valid(name):
                        key, value = self._enum(name)
                    else:
                        key, value = self._not_enum(name)
                    result[key] = value
                return Item.Metadata(result)

    def __getitem__(self, query: Query) -> typing.Iterable[Row]:
        get = self.Get(rows=self, query=query)
        return (
            Row(
                kind=query.mask.kind,
                status=get.status(r),
                chain=r.chain,
                created=Item.Created(
                    datetime.datetime.fromisoformat(r.created).replace(
                        tzinfo=datetime.UTC
                    )
                ),
                reserver=Item.Reserver(r.reserver)
                if bool(r.reserver)
                else Item.Reserver(None),
                digest=Item.Data.Digest.from_base64(r.digest),
                metadata=get.Metadata(source=get, row=r)(),
            )
            for r in get.raw
        )

    def __setitem__(self, old: Row, new: Row) -> None:
        if not (changes := new.sub(old, self._enums)):
            return

        name = self.table(old.kind)

        for _ in range(2):
            try:
                with self._connect() as connection:
                    connection.execute(
                        sqlalchemy.text(
                            f"update {name} set {self._set(changes)} "
                            f"where {self._where_string(old)}"
                        )
                    )
                break
            except Exception:
                with self._connect() as connection:
                    Table(
                        connection=connection,
                        name=name,
                        fields=Fields.Fields(
                            row=new,
                            db=self.db,
                            table=old.kind,
                            transform=self.table,
                            enums=self._enums,
                        ).fields,
                    )

    def __delitem__(self, row: Row) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    sqlalchemy.text(
                        f"delete from {self.table(row.kind)} "
                        f"where {self._where_string(row)}"
                    )
                )
        except Exception:
            """"""

    @contextlib.contextmanager
    def transaction(self) -> typing.Iterator[typing.Self]:
        with self._connect() as connection:
            yield dataclasses.replace(self, connection=connection)

    @contextlib.contextmanager
    def _connect(self) -> typing.Iterator[sqlalchemy.Connection]:
        match self.connection:
            case sqlalchemy.Connection():
                if self.connection.closed:
                    with self.db.begin() as connection:
                        yield connection
                else:
                    with self.connection.begin_nested() as _:
                        yield self.connection
            case None:
                with self.db.begin() as connection:
                    yield connection

    def __contains__(self, row: Row) -> bool:
        with self._connect() as connection:
            try:
                return connection.execute(
                    sqlalchemy.text(
                        f"select (exists (select * from {self.table(row.kind)} "
                        f"where {self._where_string(row)}))"
                    )
                ).scalar_one()
            except Exception:
                return False

    def __len__(self) -> int:
        with self._connect() as connection:
            return sum(
                connection.execute(
                    sqlalchemy.text(f"SELECT COUNT(*) from {name}")
                ).scalar_one()
                for name in sqlalchemy.inspect(connection).get_table_names()
                if (~self.table).valid(name)
            )

    def clear(self) -> None:
        self._cache.clear()
        with self._connect() as connection:
            for name in sqlalchemy.inspect(connection).get_table_names():
                if (~self.table).valid(name):
                    connection.execute(sqlalchemy.text(f"DROP TABLE {name}"))
