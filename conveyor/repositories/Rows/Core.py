from __future__ import annotations

import typing
import pydantic
import sqlalchemy
import contextlib

from .Table import Table
from ...core import Item, Query
from ...core.Item import Base64String



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Row:

	type:          Item.Type
	status:        Item.Status

	digest:        Item.Data.Digest
	metadata:      Item.Metadata

	chain:         str
	created:       Item.Created
	reserver:      Item.Reserver

	@pydantic.validator('metadata')
	def metadata_valid(cls, metadata: Item.Metadata, values: dict[str, Item.Value | Item.Metadata.Value]) -> Item.Metadata:
		for k in metadata.value:
			if k.value in values:
				raise KeyError(f'Field name "{k.value}" reserved and can not be used in metadata')
		return metadata

	@classmethod
	@pydantic.validate_arguments
	def from_item(cls, item: Item) -> typing.Self:
		return Row(**({
			k: v
			for k, v in item.__dict__.items()
			if k not in ['data', 'chain']
		} | {
			'digest': item.data.digest,
			'chain': item.chain.value
		}))

	@property
	def dict_(self) -> dict[str, Item.Metadata.Value]:
		return dict[str, Item.Metadata.Value]({
			'chain':    self.chain,
			'status':   self.status.value,
			'digest':   self.digest.string,
			'created':  self.created.value,
			'reserver': self.reserver.value
		}) | {
			word.value: value
			for word, value in self.metadata.value.items()
		}


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
		with self.connect(nested=False) as connection:
			connection.execute(
				Table(
					connection=connection,
					name=row.type,
					metadata=row.metadata
				).insert().values((row.dict_,))
			)


	@pydantic.validate_arguments
	def __getitem__(self, item_query: Query) -> typing.Iterable[Row]:

		with self.connect() as connection:

			t = Table(connection, item_query.mask.type)

			for r in connection.execute(
				sqlalchemy.sql
				.select(t)
				.where(*self._where(item_query.mask))
				.limit(item_query.limit)
			):

				yield Row(
					type=item_query.mask.type,
					status=Item.Status(r.status),
					chain=r.chain,
					created=Item.Created(r.created),
					reserver=Item.Reserver(
						exists=bool(r.reserver),
						value=r.reserver
					),
					digest=Item.Data.Digest(Base64String(r.digest)),
					metadata=Item.Metadata({
						Item.Metadata.Key(name): getattr(r, name)
						for name in t.columns.keys()
						if not (name in Item.__dataclass_fields__ or name in ('id', 'digest'))
					})
				)

	@pydantic.validate_arguments
	def __setitem__(self, old: Row, new: Row) -> None:
		with self.connect() as connection:
			t = Table(connection, old.type)
			connection.execute(
				sqlalchemy.sql.update(t).where(*self._where(old)).values(**new.dict_)
			)

	@pydantic.validate_arguments
	def __delitem__(self, row: Row) -> None:
		with self.connect() as connection:
			t = Table(connection, row.type)
			connection.execute(
				sqlalchemy.sql.delete(t).where(*self._where(row))
			)


	@pydantic.validate_arguments
	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:
		with self.connect() as connection:
			yield Core(self.db, connection)


	@pydantic.validate_arguments
	@contextlib.contextmanager
	def connect(self, nested: bool = True) -> typing.Iterator[sqlalchemy.Connection]:
		match self.connection:
			case sqlalchemy.Connection():
				if nested:
					with self.connection.begin_nested() as c:
						yield self.connection
						c.rollback()
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

	@pydantic.validate_arguments
	def __len__(self) -> pydantic.NonNegativeInt:

		result: pydantic.NonNegativeInt = 0

		with self.connect() as c:
			names = sqlalchemy.inspect(c).get_table_names()

		with self.connect() as connection:
			for name in names:
				if name.startswith('conveyor_'):
					result += connection.execute(
						sqlalchemy.sql.select(sqlalchemy.func.count()).select_from(
							Table(connection, Item.Type(name[9:]))
						)
					).scalar_one()

		return result