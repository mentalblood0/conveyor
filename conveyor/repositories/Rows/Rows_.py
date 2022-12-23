from __future__ import annotations

import peewee
import typing
import pydantic

from ...core import Item, ItemQuery
from ...core.Item import Base64String
from ...common.Model import Model, metadata_fields, BaseModel



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
	def from_item(cls, item: Item):
		return Row(**({
			k: v
			for k, v in item.__dict__.items()
			if k not in ['data', 'chain']
		} | {
			'digest': item.data.digest,
			'chain': item.chain.value
		}))


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Rows_:

	Item = Row

	db: peewee.Database

	class OperationalError(KeyError):
		@pydantic.validate_arguments
		def __init__(self, row: Row, action: str, changes_number: int):
			super().__init__(f'{changes_number} (expected 1) changes during {action} of row {row}')

	@pydantic.validate_arguments
	def _row(self, row: Row) -> dict[str, Item.Metadata.Value]:
		return dict[str, Item.Metadata.Value]({
			'status': row.status.value,
			'chain': row.chain,
			'created': row.created.value,
			'reserver': row.reserver.value,
			'digest': row.digest.string
		}) | {
			word.value: value
			for word, value in row.metadata.value.items()
		}

	@pydantic.validate_arguments
	def _model(self, row: Row) -> type[BaseModel]:
		return Model(
			db=self.db,
			name=row.type,
			metadata_columns={
				k: metadata_fields[type(v)]()
				for k, v in row.metadata.value.items()
			}
		)

	@pydantic.validate_arguments
	def _check(self, row: Row, action: str, result: int):
		if result != 1:
			raise Rows_.OperationalError(row, action, result)

	@pydantic.validate_arguments
	def _where(self, model: type[BaseModel], row: Row) -> typing.Iterable[object]:
		result: list[object] = [
			model.status   == row.status.value,
			model.digest   == row.digest.string,
			model.chain    == row.chain,
			model.created  == row.created.value,
			model.reserver == row.reserver.value
		] + [
			getattr(model, k.value)==v
			for k, v in row.metadata.value.items()
		]
		return result

	@pydantic.validate_arguments
	def add(self, row: Row) -> None:
		self._model(row).insert(**self._row(row)).execute()

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Row]:

		model = Model(self.db, item_query.mask.type)

		db_query = model.select()

		if conditions := [
			getattr(model, k)==v
			for k, v in item_query.mask.conditions.items()
			if k not in ['type', 'data']
		]:
			db_query = db_query.where(*conditions)

		db_query = db_query.limit(item_query.limit)

		for r in db_query:
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
					for name in r.__data__
					if not (name in Item.__dataclass_fields__ or name in ['id', 'digest'])
				})
			)

	@pydantic.validate_arguments
	def __setitem__(self, old: Row, new: Row) -> None:
		model = Model(self.db, old.type)
		self._check(old, 'update', model.update(**self._row(new)).where(*self._where(model, old)).execute())

	@pydantic.validate_arguments
	def __delitem__(self, row: Row) -> None:
		model = Model(self.db, row.type)
		self._check(row, 'delete', model.delete().where(*self._where(model, row)).execute())

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable[[], None]) -> None:
		with self.db.transaction():
			f()

	@pydantic.validate_arguments
	def _clear(self, type: Item.Type) -> None:
		self.db.drop_tables([
			Model(self.db, type)
		])