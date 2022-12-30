from __future__ import annotations

import typing
import pydantic
import sqlalchemy

from ...core import Item, Query
from ...common.Table import Table
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
			'status': self.status.value,
			'chain': self.chain,
			'created': self.created.value,
			'reserver': self.reserver.value,
			'digest': self.digest.string
		}) | {
			word.value: value
			for word, value in self.metadata.value.items()
		}


def Conditions(mask: Query.Mask) -> dict[str, Item.Value]:

	result: dict[str, Item.Value] = {}

	if mask.type is not None:
		result['type'] = mask.type.value
	if mask.status is not None:
		result['status'] = mask.status.value
	if mask.data is not None:
		result['data'] = mask.data.string
		result['digest'] = mask.data.digest.string
	elif mask.digest is not None:
		result['digest'] = mask.digest.string

	if mask.metadata is not None:
		for k, v in mask.metadata.value.items():
			result[k.value] = v

	if mask.chain is not None:
		result['chain'] = mask.chain.value
	if mask.created is not None:
		result['created'] = mask.created.value
	if mask.reserver is not None:
		result['reserver'] = mask.reserver.value

	return result


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Rows_:

	Item = Row

	db: sqlalchemy.engine.Engine

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def _where(self, row: Row) -> typing.Iterable[sqlalchemy.sql.expression.ColumnElement[bool]]:
		yield     sqlalchemy.column('status')   == row.status.value
		yield     sqlalchemy.column('digest')   == row.digest.string
		yield     sqlalchemy.column('chain')    == row.chain
		yield     sqlalchemy.column('created')  == row.created.value
		yield     sqlalchemy.column('reserver') == row.reserver.value
		for k, v in row.metadata.value.items():
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

		db_query = sqlalchemy.sql.select(t)

		if conditions := [
			getattr(t.c, k) == v
			for k, v in Conditions(item_query.mask).items()
			if k not in ['type', 'data']
		]:
			db_query = db_query.where(*conditions)

		db_query = db_query.limit(item_query.limit)

		with self.db.connect() as connection:

			for r in connection.execute(db_query):

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
						for name in r._mapping
						if not (name in Item.__dataclass_fields__ or name in ('id', 'digest'))
					})
				)

	@pydantic.validate_arguments
	def __setitem__(self, old: Row, new: Row) -> None:
		t = Table(self.db, old.type)
		with self.db.connect() as connection:
			connection.execute(
				sqlalchemy.sql.update(t).where(*self._where(old)).values(new.dict_)
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