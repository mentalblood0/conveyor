from __future__ import annotations

import typing
import pydantic
import functools
import sqlalchemy
import contextlib
import dataclasses
import sqlalchemy.exc

from ....core import Item, Query, Transforms

from .Row import Row
from .Table import Table
from .Enum import DbEnumName, Enum
from .Field import fields, columns
from .DbTableName import DbTableName



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Core:

	Item = Row

	db: sqlalchemy.engine.Engine
	connection: sqlalchemy.Connection | None = None

	table: Transforms.Safe[Item.Type, str] = DbTableName('conveyor')
	enum:  Transforms.Safe[Item.Key,  str] = DbEnumName('enum')

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def _where(self, ref: Row | Query.Mask) -> typing.Iterable[sqlalchemy.sql.expression.ColumnElement[bool]]:
		if ref.status is not None:
			status = Enum(
				name_ = Item.Key('status'),
				transform = self.enum
			)
			yield     status.column                 == status.Int(functools.partial(self.connect, nested = True), ref.type.value)(ref.status.value)
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
				match v:
					case Item.Metadata.Enumerable():
						enumerable = Enum(
							name_     = k,
							transform = self.enum
						)
						yield enumerable.column     == enumerable.Int(functools.partial(self.connect, nested = True), ref.type.value)(v.value)
					case _:
						yield sqlalchemy.column(k.value)    == v

	@pydantic.validate_arguments
	def append(self, row: Row) -> None:

		name = self.table(row.type)

		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						name,
						sqlalchemy.MetaData(),
						*columns(row.metadata, self.db, name, self.enum)
					).insert().values((row.dict_(self.enum, functools.partial(self.connect, nested = True), row.type.value),))
				)
		except:
			with self.connect() as connection:
				connection.execute(
					Table(
						connection = connection,
						name       = name,
						fields_    = fields(row.metadata, self.db, name, self.enum)
					).insert().values((row.dict_(self.enum, functools.partial(self.connect, nested = True), row.type.value),))
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

				status = Enum(
					name_     = Item.Key('status'),
					transform = self.enum
				)

				metadata: dict[Item.Metadata.Key, Item.Metadata.Value] = {}
				for name in r.__getstate__()['_parent'].__getstate__()['_keys']:
					if not (
						name in Item.__dataclass_fields__
						or
						name in ('id', 'digest', status.name)
					):
						if (~self.enum).valid(name):
							unenumed = (~self.enum)(name)
							metadata[unenumed] = Item.Metadata.Enumerable(
								Enum(
									name_     = unenumed,
									transform = self.enum
								).String(
									connect   = functools.partial(self.connect, nested = True),
									table     = query.mask.type.value
								)(getattr(r, name))
							)
						else:
							metadata[Item.Metadata.Key(name)] = getattr(r, name)

				yield Row(
					type     = query.mask.type,
					status   = Item.Status(status.String(functools.partial(self.connect, nested = True), query.mask.type.value)(getattr(r, status.name))),
					chain    = r.chain,
					created  = Item.Created(r.created),
					reserver = Item.Reserver(
						exists = bool(r.reserver),
						value  = r.reserver
					),
					digest   = Item.Data.Digest(Item.Data.Digest.Base64String(r.digest)),
					metadata = Item.Metadata(metadata)
				)

	@pydantic.validate_arguments
	def __setitem__(self, old: Row, new: Row) -> None:

		if not (changes := new.sub(old, self.enum, functools.partial(self.connect, nested = True), old.type.value)):
			return

		name = self.table(old.type)

		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						name,
						sqlalchemy.MetaData(),
						*columns(new.metadata, self.db, name, self.enum)
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
							name       = name,
							fields_    = fields(old.metadata, self.db, name, self.enum)
						)
					)
					.where(*self._where(old))
					.values(**changes)
				)

	@pydantic.validate_arguments
	def __delitem__(self, row: Row) -> None:

		name = self.table(row.type)

		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						name,
						sqlalchemy.MetaData(),
						*columns(row.metadata, self.db, name, self.enum)
					)
					.delete()
					.where(*self._where(row))
				)
		except:
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

		name = self.table(row.type)

		with self.connect() as connection:
			try:
				return connection.execute(
					sqlalchemy.sql.exists(
						Table(connection, name, fields(row.metadata, self.db, name, self.enum))
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