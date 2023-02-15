from __future__ import annotations

import typing
import pydantic
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



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Core:

	Item = Row

	db         : sqlalchemy.engine.Engine
	connection : sqlalchemy.Connection | None            = None

	table      : Transforms.Safe[Item.Type,         str] = DbTableName('conveyor')
	enum       : Transforms.Safe[Item.Key, str]          = DbEnumName('enum')

	@property
	def _cache_id(self) -> str:
		return str(self.db)

	@property
	def _cache(self) -> Cache.Enums.Cache:
		return Cache.cache[self._cache_id]

	@property
	def _enums(self) -> Enums.Enums:
		return Enums.Enums(
			connect        = self._connect,
			type_transform = self.table,
			enum_transform = self.enum,
			cache_id       = self._cache_id
		)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def _where(self, ref: Row | Query.Mask) -> typing.Iterable[sqlalchemy.sql.expression.ColumnElement[bool]]:
		if ref.status is not None:
			yield self._enums[(ref.type, Item.Key('status'))].eq(ref.status)
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
						yield      self._enums[(ref.type, Item.Key(k.value))].eq(v)
					case _:
						yield     sqlalchemy.column(k.value) == v

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def _where_string(self, ref: Row | Query.Mask) -> str:
		return ' and '.join(
			str(
				c.compile(
					bind           = self.db,
					compile_kwargs = {"literal_binds": True}
				)
			)
			for c in self._where(ref)
		)

	@pydantic.validate_arguments
	def append(self, row: Row) -> None:

		fields = Fields.Fields(
			row       = row,
			db        = self.db,
			table     = row.type,
			transform = self.table,
			enums     = self._enums
		)

		name = self.table(row.type)

		print(f'-----------------------------------FIELDS {[f.name.value for f in fields.fields]}')
		print(f'-----------------------------------DICT {[r for r in row.dict_(self._enums).keys()]}')

		try:
			with self._connect() as connection:
				connection.execute(
					sqlalchemy.Table(
						name,
						sqlalchemy.MetaData(),
						*fields.columns
					)
					.insert()
					.values((row.dict_(self._enums),))
				)
		except:
			with self._connect() as connection:
				connection.execute(
					Table(
						connection = connection,
						name       = name,
						fields     = fields.fields
					).insert().values((row.dict_(self._enums),))
				)


	@pydantic.validate_arguments
	def __getitem__(self, query: Query) -> typing.Iterable[Row]:

		q = (
			sqlalchemy.sql
			.select(sqlalchemy.text('*'))
			.select_from(sqlalchemy.text(self.table(query.mask.type)))
			.where(*self._where(query.mask))
		)
		if query.limit is not None:
			q = q.limit(query.limit)

		with self._connect() as connection:
			rows = (*connection.execute(q),)

		for r in rows:

			status = self._enums[(query.mask.type, Item.Key('status'))]

			metadata: dict[Item.Metadata.Key, Item.Metadata.Value] = {}
			for name in r.__getstate__()['_parent'].__getstate__()['_keys']:
				if not (
					name in (f.name for f in dataclasses.fields(Item))
					or
					name in ('id', 'digest', status.db_field)
				):
					if (~self.enum).valid(name):
						match value := getattr(r, name):
							case int() | None:
								unenumed = (~self.enum)(name)
								metadata[Item.Metadata.Key(unenumed.value)] = self._enums[(query.mask.type, unenumed)].convert(value)
							case _:
								raise ValueError(f'Expected column `{name}` in table `{query.mask.type.value}` to hold enumerable using integer or null value')
					else:
						metadata[Item.Metadata.Key(name)] = getattr(r, name)

			if (status_value := status.String(getattr(r, status.db_field)).value) is None:
				raise ValueError(f'Status value can not be None')

			yield Row(
				type     = query.mask.type,
				status   = Item.Status(status_value),
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

		if not (changes := new.sub(old, self._enums)):
			return

		fields = Fields.Fields(
			row  = new,
			db        = self.db,
			table     = old.type,
			transform = self.table,
			enums     = self._enums
		)

		name = self.table(old.type)

		try:
			with self._connect() as connection:
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
			with self._connect() as connection:
				connection.execute(
					sqlalchemy.sql
					.update(
						Table(
							connection = connection,
							name       = name,
							fields     = fields.fields
						)
					)
					.where(*self._where(old))
					.values(**changes)
				)

	@pydantic.validate_arguments
	def __delitem__(self, row: Row) -> None:
		try:
			with self._connect() as connection:
				connection.execute(sqlalchemy.text(
					f'delete from {self.table(row.type)} where {self._where_string(row)}'
				))
		except:
			pass

	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:
		with self._connect() as connection:
			yield dataclasses.replace(self, connection=connection)

	@pydantic.validate_arguments
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

	@pydantic.validate_arguments
	def __contains__(self, row: Row) -> bool:
		with self._connect() as connection:
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
		with self._connect() as connection:
			return sum(
				connection.execute(sqlalchemy.text(f'SELECT COUNT(*) from {name}')).scalar_one()
				for name in sqlalchemy.inspect(connection).get_table_names()
				if (~self.table).valid(name)
			)

	def clear(self) -> None:
		self._cache.clear()
		with self._connect() as connection:
			for name in sqlalchemy.inspect(connection).get_table_names():
				if (~self.table).valid(name):
					connection.execute(sqlalchemy.text(f'DROP TABLE {name}'))