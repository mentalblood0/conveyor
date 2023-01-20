from __future__ import annotations

import typing
import pydantic
import functools
import contextlib
import sqlalchemy
import dataclasses
import sqlalchemy.exc

from ....core import Item, Query, Transforms

from . import Cache
from .Row import Row
from .Table import Table
from . import Enums, Fields
from .DbEnumName import DbEnumName
from .DbTableName import DbTableName



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Core:

	Item = Row

	db: sqlalchemy.engine.Engine
	connection: sqlalchemy.Connection | None = None

	table: Transforms.Safe[Item.Type, str] = DbTableName('conveyor')
	enum:  Transforms.Safe[Item.Key,  str] = DbEnumName('enum')

	@property
	def cache_id(self):
		return str(self.db)

	@property
	def cache(self):
		return Cache.cache[self.cache_id]

	@property
	def enums(self):
		return Enums.Enums(
			connect        = functools.partial(self.connect, nested = True),
			type_transform = self.table,
			enum_transform = self.enum,
			cache_id       = self.cache_id
		)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def _where(self, ref: Row | Query.Mask) -> typing.Iterable[sqlalchemy.sql.expression.ColumnElement[bool]]:
		if ref.status is not None:
			yield self.enums[(ref.type, Item.Key('status'))].eq(Item.Metadata.Enumerable(ref.status.value))
		if ref.digest is not None:
			yield                sqlalchemy.column('digest') == ref.digest.string
		match ref.chain:
			case None:
				pass
			case str():
				yield             sqlalchemy.column('chain') == ref.chain
			case _:
				yield             sqlalchemy.column('chain') == ref.chain.value
		if ref.created is not None:
			yield               sqlalchemy.column('created') == ref.created.value
		if ref.reserver is not None:
			yield              sqlalchemy.column('reserver') == ref.reserver.value
		if ref.metadata is not None:
			for k, v in ref.metadata.value.items():
				match v:
					case Item.Metadata.Enumerable():
						yield      self.enums[(ref.type, k)].eq(v)
					case _:
						yield     sqlalchemy.column(k.value) == v

	@pydantic.validate_arguments
	def append(self, row: Row) -> None:

		fields = Fields.Fields(
			metadata  = row.metadata,
			db        = self.db,
			table     = row.type,
			transform = self.table,
			enums     = self.enums
		)

		name = self.table(row.type)

		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						name,
						sqlalchemy.MetaData(),
						*fields.columns
					)
					.insert()
					.values((row.dict_(self.enums),))
				)
		except:
			with self.connect() as connection:
				connection.execute(
					Table(
						connection = connection,
						name       = name,
						fields_    = fields.fields
					).insert().values((row.dict_(self.enums),))
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

				status = self.enums[(query.mask.type, Item.Key('status'))]

				metadata: dict[Item.Metadata.Key, Item.Metadata.Value] = {}
				for name in r.__getstate__()['_parent'].__getstate__()['_keys']:
					if not (
						name in Item.__dataclass_fields__
						or
						name in ('id', 'digest', status.db_field)
					):
						if (~self.enum).valid(name):
							unenumed = (~self.enum)(name)
							metadata[Item.Metadata.Key(unenumed.value)] = self.enums[(query.mask.type, unenumed)].String(getattr(r, name))
						else:
							metadata[Item.Metadata.Key(name)] = getattr(r, name)

				yield Row(
					type     = query.mask.type,
					status   = Item.Status(status.String(getattr(r, status.db_field)).value),
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

		if not (changes := new.sub(old, self.enums)):
			return

		fields = Fields.Fields(
			metadata  = new.metadata,
			db        = self.db,
			table     = old.type,
			transform = self.table,
			enums     = self.enums
		)

		name = self.table(old.type)

		try:
			with self.connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						name,
						sqlalchemy.MetaData(),
						*fields.columns
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
							fields_    = fields.fields
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
						*Fields.Fields(
							metadata  = row.metadata,
							db        = self.db,
							table     = row.type,
							transform = self.table,
							enums     = self.enums
						).columns
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
		with self.connect() as connection:
			try:
				return connection.execute(
					sqlalchemy.sql.exists(
						sqlalchemy.sql.select('*')
						.select_from(sqlalchemy.text(self.table(row.type)))
						.where(*self._where(row))
					).select()
				).scalar_one()
			except:
				return False

	def __len__(self) -> pydantic.NonNegativeInt:
		with self.connect() as connection:
			return sum(
				connection.execute(sqlalchemy.text(f'SELECT COUNT(*) from {name}')).scalar_one()
				for name in sqlalchemy.inspect(connection).get_table_names()
				if (~self.table).valid(name)
			)

	def clear(self) -> None:
		self.cache.clear()
		with self.connect() as connection:
			for name in sqlalchemy.inspect(connection).get_table_names():
				if (~self.table).valid(name):
					connection.execute(sqlalchemy.text(f'DROP TABLE {name}'))