from __future__ import annotations

import typing
import pydantic
import sqlalchemy
import contextlib
import dataclasses
import sqlalchemy.exc

from .Table import Table
from ...core import Item, Query
from .Field import Field, base_fields
from ...core.Item import Base64String



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Row:

	type:     Item.Type
	status:   Item.Status

	digest:   Item.Data.Digest
	metadata: Item.Metadata

	chain:    str
	created:  Item.Created
	reserver: Item.Reserver

	@pydantic.validator('metadata')
	def metadata_valid(cls, metadata: Item.Metadata, values: dict[str, Item.Value | Item.Metadata.Value]) -> Item.Metadata:
		for k in metadata.value:
			if k.value in values:
				raise KeyError(f'Field name "{k.value}" reserved and can not be used in metadata')
		return metadata

	@classmethod
	@pydantic.validate_arguments
	def from_item(cls, item: Item) -> typing.Self:
		return Row(
			type     = item.type,
			status   = item.status,
			digest   = item.data.digest,
			chain    = item.chain.value,
			created  = item.created,
			reserver = item.reserver,
			metadata = item.metadata
		)

	@property
	def dict_(self) -> dict[str, Item.Metadata.Value]:
		return {
			'chain':    self.chain,
			'status':   self.status.value,
			'digest':   self.digest.string,
			'created':  self.created.value,
			'reserver': self.reserver.value,
			**{
				word.value: value
				for word, value in self.metadata.value.items()
			}
		}

	def __sub__(self, another: 'Row') -> dict[str, Item.Metadata.Value]:

		result: dict[str, Item.Metadata.Value] = {}

		if self.status != another.status:
			result['status'] = self.status.value
		if self.digest != another.digest:
			result['digest'] = self.digest.string
		if self.chain != another.chain:
			result['chain'] = self.chain
		if self.created != another.created:
			result['created'] = self.created.value
		if self.reserver != another.reserver:
			result['reserver'] = self.reserver.value

		result |= {
			k.value: v
			for k, v in self.metadata.value.items()
			if self.metadata.value[k] != another.metadata.value[k]
		}

		return result


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Core:

	Item = Row

	db: sqlalchemy.engine.Engine
	connection: sqlalchemy.Connection | None = None

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
						f'conveyor_{row.type.value}',
						sqlalchemy.MetaData(),
						*{
							Field(name_ = n, value = None).column
							for n in base_fields
						},
						*{
							Field(name_ = k, value = v).column
							for k, v in row.metadata.value.items()
						}
					).insert().values((row.dict_,))
				)
		except:
			with self.connect() as connection:
				connection.execute(
					Table(
						connection = connection,
						name       = row.type,
						metadata   = row.metadata
					).insert().values((row.dict_,))
				)


	@pydantic.validate_arguments
	def __getitem__(self, query: Query) -> typing.Iterable[Row]:
		with self.connect() as connection:
			for r in connection.execute(
				sqlalchemy.sql
				.select(sqlalchemy.text('*'))
				.select_from(sqlalchemy.text(f'conveyor_{query.mask.type.value}'))
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
					digest   = Item.Data.Digest(Base64String(r.digest)),
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
						f'conveyor_{old.type.value}',
						sqlalchemy.MetaData(),
						*(
							Field(name_ = n, value = None).column
							for n in base_fields
						),
						*(
							Field(name_ = k, value = v).column
							for k, v in new.metadata.value.items()
						)
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
							name       = old.type,
							metadata   = old.metadata
						)
					)
					.where(*self._where(old))
					.values(**changes)
				)

	@pydantic.validate_arguments
	def __delitem__(self, row: Row) -> None:
		with self.connect() as connection:
			connection.execute(
				sqlalchemy.Table(
					f'conveyor_{row.type.value}',
					sqlalchemy.MetaData(),
					*(
						Field(name_ = n, value = None).column
						for n in base_fields
					),
					*(
						Field(name_ = k, value = v).column
						for k, v in row.metadata.value.items()
					)
				)
				.delete()
				.where(*self._where(row))
			)


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
						Table(connection, row.type, row.metadata)
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
				if name.startswith('conveyor_')
			)

	def clear(self) -> None:
		with self.connect() as connection:
			for name in sqlalchemy.inspect(connection).get_table_names():
				if name.startswith('conveyor_'):
					connection.execute(sqlalchemy.text(f'DROP TABLE {name}'))