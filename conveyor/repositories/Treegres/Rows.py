from __future__ import annotations

import peewee
import pydantic

from ...core import Item, Word
from ...common.Model import Model, BaseModel, metadata_fields



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class RowsItem:

	value: Item

	@pydantic.validator('value')
	def value_correct(cls, value):
		for k in value.metadata.value:
			if hasattr(value, k.value):
				raise KeyError(f'Field name "{k}" reserved and can not be used in metadata')
		return value


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Rows:

	db: peewee.Database

	class OperationalError(Exception):
		@pydantic.validate_arguments
		def __init__(self, item: RowsItem, action: str):
			super().__init__(f'Item {action} (type={item.value.type}, status={item.value.status}, digest={item.value.data.digest.string}) had no result')

	@pydantic.validate_arguments
	def _row(self, item: RowsItem) -> dict[str, Item.Metadata.Value]:
		return {
			'status': item.value.status.value,
			'chain': item.value.chain.value
		} | {
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
	def save(self, item: RowsItem) -> None:
		if self._model(item)(**self._row(item)).save(force_insert=True) != 1:
			raise Rows.OperationalError(item, 'save')

	def update(self, old: RowsItem, new: RowsItem) -> None:

		model = Model(self.db, old.value.type)

		if (
			model
			.update(**self._row(new))
			.where(self._where(model, old)).execute()
		) != 1:
			raise Rows.OperationalError(old, 'update')

	@pydantic.validate_arguments
	def unreserve(self, item: RowsItem) -> None:
		model = Model(self.db, item.value.type)
		model.update(reserved=None).where(self._where(model, item)).execute()

	@pydantic.validate_arguments
	def delete(self, item: RowsItem) -> None:
		model = Model(self.db, item.value.type)
		model.delete().where(self._where(model, item)).execute()

	@pydantic.validate_arguments
	def _clear(self, type: Item.Type):
		self.db.drop_tables([
			Model(self.db, type)
		])