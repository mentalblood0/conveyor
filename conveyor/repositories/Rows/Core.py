from __future__ import annotations

import typing
import pydantic
import sqlalchemy

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
	def add(self, row: Row) -> None:
		with self.db.connect() as connection:
			connection.execute(
				Table(
					db=self.db,
					name=row.type,
					metadata=row.metadata
				).insert().values((row.dict_,))
			)
			connection.commit()

	@pydantic.validate_arguments
	def __getitem__(self, item_query: Query) -> typing.Iterable[Row]:

		t = Table(self.db, item_query.mask.type)

		with self.db.connect() as connection:

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
		t = Table(self.db, old.type)
		with self.db.connect() as connection:
			connection.execute(
				sqlalchemy.sql.update(t).where(*self._where(old)).values(**new.dict_)
			)
			connection.commit()

	@pydantic.validate_arguments
	def __delitem__(self, row: Row) -> None:
		t = Table(self.db, row.type)
		with self.db.connect() as connection:
			connection.execute(
				sqlalchemy.sql.delete(t).where(*self._where(row))
			)
			connection.commit()