from __future__ import annotations

import typing
import pydantic
import sqlalchemy
import contextlib
import dataclasses
import sqlalchemy.exc

from ....core import Item, Query, Transforms

from .Row import Row
from .Table import Table
from .Field import fields, columns



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class DbTableName(Transforms.Safe[Item.Type, str]):

	prefix: str

	@pydantic.validate_arguments
	def transform(self, i: Item.Type) -> str:
		return f'{self.prefix}_{i.value}'

	def __invert__(self) -> 'ItemType':
		return ItemType(self.prefix)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class ItemType(Transforms.Safe[str, Item.Type]):

	prefix: str

	@pydantic.validate_arguments
	def transform(self, i: str) -> Item.Type:
		return Item.Type(i[len(self.prefix) + 1:])

	def __invert__(self) -> DbTableName:
		return DbTableName(self.prefix)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Core:

	Item = Row

	db: sqlalchemy.engine.Engine
	connection: sqlalchemy.Connection | None = None

	table: Transforms.Safe[Item.Type, str] = DbTableName('conveyor')

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def _where(self, ref: Row | Query.Mask) -> typing.Iterable[sqlalchemy.sql.expression.ColumnElement[bool]]:
		if ref.status is not None:
			yield     sqlalchemy.column('status')   == ref.status.value
		if ref.digest is not None:
			yield     sqlalchemy.column('digest')   == ref.digest.string
		match ref.chain:
			case None:
				pass
			case str():
				yield sqlalchemy.column('chain')    == ref.chain
			case _:
				yield sqlalchemy.column('chain')    == ref.chain.value
		if ref.created is not None:
			yield     sqlalchemy.column('created')  == ref.created.value
		if ref.reserver is not None:
			yield     sqlalchemy.column('reserver') == ref.reserver.value
		if ref.metadata is not None:
			for k, v in ref.metadata.value.items():
				yield sqlalchemy.column(k.value)    == v

	@pydantic.validate_arguments
	def append(self, row: Row) -> None:
		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						self.table(row.type),
						sqlalchemy.MetaData(),
						*columns(row.metadata)
					).insert().values((row.dict_,))
				)
		except:
			with self.connect() as connection:
				connection.execute(
					Table(
						connection = connection,
						name       = self.table(row.type),
						fields_    = fields(row.metadata)
					).insert().values((row.dict_,))
				)


	@pydantic.validate_arguments
	def __getitem__(self, query: Query) -> typing.Iterable[Row]:
		with self.connect() as connection:
			for r in connection.execute(
				sqlalchemy.sql
				.select(sqlalchemy.text('*'))
				.select_from(sqlalchemy.text(self.table(query.mask.type)))
				.where(*self._where(query.mask))
				.limit(query.limit)
			):
				yield Row(
					type     = query.mask.type,
					status   = Item.Status(r.status),
					chain    = r.chain,
					created  = Item.Created(r.created),
					reserver = Item.Reserver(
						exists = bool(r.reserver),
						value  = r.reserver
					),
					digest   = Item.Data.Digest(Item.Data.Digest.Base64String(r.digest)),
					metadata = Item.Metadata({
						Item.Metadata.Key(name): getattr(r, name)
						for name in r.__getstate__()['_parent'].__getstate__()['_keys']
						if not (
							name in Item.__dataclass_fields__
							or
							name in ('id', 'digest')
						)
					})
				)

	@pydantic.validate_arguments
	def __setitem__(self, old: Row, new: Row) -> None:

		if not (changes := new - old):
			return

		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						self.table(old.type),
						sqlalchemy.MetaData(),
						*columns(new.metadata)
					)
					.update()
					.where(*self._where(old))
					.values(**changes)
				)
		except:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.sql
					.update(
						Table(
							connection = connection,
							name       = self.table(old.type),
							fields_    = fields(old.metadata)
						)
					)
					.where(*self._where(old))
					.values(**changes)
				)

	@pydantic.validate_arguments
	def __delitem__(self, row: Row) -> None:
		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						self.table(row.type),
						sqlalchemy.MetaData(),
						*columns(row.metadata)
					)
					.delete()
					.where(*self._where(row))
				)
		except sqlalchemy.exc.OperationalError:
			pass


	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:
		with self.connect() as connection:
			yield dataclasses.replace(self, connection=connection)


	@pydantic.validate_arguments
	@contextlib.contextmanager
	def connect(self, nested: bool = True) -> typing.Iterator[sqlalchemy.Connection]:
		match self.connection:
			case sqlalchemy.Connection():
				if nested:
					with self.connection.begin_nested() as c:
						yield self.connection
				else:
					yield self.connection
			case None:
				with self.db.begin() as c:
					yield c

	@pydantic.validate_arguments
	def __contains__(self, row: Row) -> bool:
		with self.connect() as connection:
			try:
				return connection.execute(
					sqlalchemy.sql.exists(
						Table(connection, self.table(row.type), fields(row.metadata))
						.select()
						.where(*self._where(row))
					).select()
				).scalar_one()
			except KeyError:
				return False

	def __len__(self) -> pydantic.NonNegativeInt:
		with self.connect() as connection:
			return sum(
				connection.execute(sqlalchemy.text(f'SELECT COUNT(*) from {name}')).scalar_one()
				for name in sqlalchemy.inspect(connection).get_table_names()
				if (~self.table).valid(name)
			)

	def clear(self) -> None:
		with self.connect() as connection:
			for name in sqlalchemy.inspect(connection).get_table_names():
				if (~self.table).valid(name):
					connection.execute(sqlalchemy.text(f'DROP TABLE {name}'))