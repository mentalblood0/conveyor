from __future__ import annotations

import peewee
import typing
import pydantic

from ...core import Item, ItemQuery, Digest, Chain, Base64String
from ...common.Model import Model, metadata_fields, BaseModel



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class RowsItem:

	value: Item

	@pydantic.validator('value')
	def value_correct(cls, value):
		for k in value.metadata.value:
			if hasattr(value, k.value):
				raise KeyError(f'Field name "{k}" reserved and can not be used in metadata')
		return value


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Row(Item):

	chain: str
	digest: Digest
	data: None = None

	@pydantic.validate_arguments
	def item(self, data: Item.Data) -> Item:
		return Item(
			type=self.type,
			status=self.status,
			data=data,
			metadata=self.metadata,
			chain=Chain(
				ref=data,
				test=self.chain
			),
			created=self.created,
			reserved=self.reserved
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Rows:

	db: peewee.Database

	class OperationalError(Exception):
		@pydantic.validate_arguments
		def __init__(self, item: RowsItem, action: str):
			super().__init__(f'Item {action} (type={item.value.type}, status={item.value.status}, digest={item.value.data.digest.string}) had no result')

	@pydantic.validate_arguments
	def _row(self, item: RowsItem) -> dict[str, Item.Metadata.Value]:
		return dict[str, Item.Metadata.Value]({
			'status': item.value.status.value,
			'chain': item.value.chain.value,
			'created': item.value.created.value,
			'reserved': item.value.reserved,
			'digest': item.value.data.digest.string
		}) | {
			word.value: value
			for word, value in item.value.metadata.value.items()
		}

	@pydantic.validate_arguments
	def _model(self, item: RowsItem) -> type[BaseModel]:
		return Model(
			db=self.db,
			name=item.value.type,
			metadata_columns={
				k: metadata_fields[type(v)]()
				for k, v in item.value.metadata.value.items()
			}
		)

	@pydantic.validate_arguments
	def _where(self, model: type[BaseModel], item: RowsItem) -> tuple:
		return (
			model.status==item.value.status.value,
			model.digest==item.value.data.digest.string,
			model.chain==item.value.chain.value,
			model.reserved==item.value.reserved
		)

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserved) -> None:

		model = Model(self.db, item_query.mask.type)

		model.update(
			reserved=reserver
		).where(
			model.digest << (
				model
				.select(model.digest)
				.where(
					model.reserved==None,
					model.status==item_query.mask.status
				)
				.order_by(peewee.fn.Random())
				.limit(item_query.limit)
			)
		).execute()

	@pydantic.validate_arguments
	def unreserve(self, item: RowsItem) -> None:
		model = Model(self.db, item.value.type)
		model.update(reserved=None).where(self._where(model, item)).execute()

	@pydantic.validate_arguments
	def add(self, item: RowsItem) -> None:
		if self._model(item).insert(**self._row(item)).execute() != 1:
			raise Rows.OperationalError(item, 'insert')

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Row]:

		model = Model(self.db, item_query.mask.type)

		db_query = model.select()

		conditions = []
		for k, v in item_query.mask.conditions.items():
			if hasattr(model, k):
				conditions.append(getattr(model, k)==v)
		if conditions:
			db_query = db_query.where(*conditions)

		db_query = db_query.limit(item_query.limit)

		for r in db_query:
			yield Row(
				type=item_query.mask.type,
				status=Item.Status(r.status),
				chain=r.chain,
				created=Item.Created(r.created),
				reserved=r.reserved,
				digest=Digest(Base64String(r.digest)),
				metadata=Item.Metadata({
					Item.Metadata.Key(name): getattr(r, name)
					for name in r.__data__
					if not (name in Item.__dataclass_fields__ or name in ['id', 'digest'])
				}),
			)

	@pydantic.validate_arguments
	def __setitem__(self, old: RowsItem, new: RowsItem) -> None:

		model = Model(self.db, old.value.type)

		if (
			model
			.update(**self._row(new))
			.where(self._where(model, old)).execute()
		) != 1:
			raise Rows.OperationalError(old, 'update')

	@pydantic.validate_arguments
	def __delitem__(self, item: RowsItem) -> None:
		model = Model(self.db, item.value.type)
		model.delete().where(*self._where(model, item)).execute()

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable[[typing.Callable], typing.Callable]:

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