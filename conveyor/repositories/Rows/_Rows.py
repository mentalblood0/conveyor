from __future__ import annotations

import peewee
import typing
import pydantic

from ...core.Item import Base64String
from ...core import Item, ItemQuery
from ...common.Model import Model, metadata_fields, BaseModel



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Row(Item):

	chain: str
	digest: Item.Data.Digest
	data: None = None
	metadata: Item.Metadata

	@pydantic.validator('metadata')
	def metadata_correct(cls, metadata, values):
		for k in metadata.value:
			if k.value in values:
				raise KeyError(f'Field name "{k.value}" reserved and can not be used in metadata')
		return metadata

	@classmethod
	@pydantic.validate_arguments
	def from_item(cls, item: Item):
		return Row(**{
			k: v
			for k, v in item.__dict__.items()
			if k not in ['data', 'chain']
		} | {
			'digest': item.data.digest,
			'chain': item.chain.value
		})


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class _Rows:

	Item = Row

	db: peewee.Database

	class OperationalError(Exception):
		@pydantic.validate_arguments
		def __init__(self, item: Row, action: str):
			super().__init__(f'Item {action} (type={item.type}, status={item.status}, digest={item.digest.string}) had no result')

	@pydantic.validate_arguments
	def _row(self, item: Row) -> dict[str, Item.Metadata.Value]:
		return dict[str, Item.Metadata.Value]({
			'status': item.status.value,
			'chain': item.chain,
			'created': item.created.value,
			'reserver': item.reserver.value,
			'digest': item.digest.string
		}) | {
			word.value: value
			for word, value in item.metadata.value.items()
		}

	@pydantic.validate_arguments
	def _model(self, item: Row) -> type[BaseModel]:
		return Model(
			db=self.db,
			name=item.type,
			metadata_columns={
				k: metadata_fields[type(v)]()
				for k, v in item.metadata.value.items()
			}
		)

	@pydantic.validate_arguments
	def _where(self, model: type[BaseModel], item: Row) -> tuple:
		return (
			model.status==item.status.value,
			model.digest==item.digest.string,
			model.chain==item.chain,
			model.reserver==item.reserver.value
		)

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserver) -> None:

		model = Model(self.db, item_query.mask.type)

		model.update(
			reserver=reserver.value
		).where(
			model.digest << (
				model
				.select(model.digest)
				.where(
					model.reserver==None,
					model.status==item_query.mask.status
				)
				.order_by(peewee.fn.Random())
				.limit(item_query.limit)
			)
		).execute()

	@pydantic.validate_arguments
	def unreserve(self, item: Row) -> None:
		model = Model(self.db, item.type)
		model.update(reserver=None).where(self._where(model, item)).execute()

	@pydantic.validate_arguments
	def add(self, item: Row) -> None:
		if self._model(item).insert(**self._row(item)).execute() != 1:
			raise _Rows.OperationalError(item, 'insert')

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Row]:

		model = Model(self.db, item_query.mask.type)

		db_query = model.select()

		if conditions := [
			getattr(model, k)==v
			for k, v in item_query.mask.conditions.items()
			if k != 'type'
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

		if (
			model
			.update(**self._row(new))
			.where(self._where(model, old)).execute()
		) != 1:
			raise _Rows.OperationalError(old, 'update')

	@pydantic.validate_arguments
	def __delitem__(self, item: Row) -> None:
		model = Model(self.db, item.type)
		model.delete().where(*self._where(model, item)).execute()

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:

		def new_f(*args, **kwargs):
			with self.db.transaction():
				result = f(*args, **kwargs)
			return result

		return new_f

	@pydantic.validate_arguments
	def _clear(self, type: Item.Type) -> None:
		self.db.drop_tables([
			Model(self.db, type)
		])