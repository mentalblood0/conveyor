from __future__ import annotations

import peewee
import pydantic

from ...core import Item
from ...common.Model import Model, BaseModel, metadata_fields



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False, config={'arbitrary_types_allowed': True})
class Rows:

	db: peewee.Database

	class OperationalError(Exception):
		@pydantic.validate_arguments
		def __init__(self, item: Rows.Item, action: str):
			super().__init__(f'Item {action} (type={item.value.type}, status={item.value.status}, digest={item.value.data.digest.string}) had no result')

	@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
	class Item:

		value: Item

		@pydantic.validator('value')
		def value_correct(cls, value):
			for k in value.metadata.value:
				if hasattr(value, k.value):
					raise KeyError(f'Field name "{k}" reserved and can not be used in metadata')
			return value

	@pydantic.validate_arguments
	def _row(self, item: Rows.Item) -> dict[str, Item.Metadata.Value]:
		return {
			'status': item.value.status.value,
			'chain': item.value.chain.value
		} | {
			word.value: value
			for word, value in item.value.metadata.value.items()
		}

	@pydantic.validate_arguments
	def _model(self, item: Rows.Item) -> type[BaseModel]:
		return Model(
			db=self.db,
			name=item.value.type,
			metadata_columns={
				k: metadata_fields[type(v)]()
				for k, v in item.value.metadata.value.items()
			}
		)

	@pydantic.validate_arguments
	def _where(self, model: type[BaseModel], item: Rows.Item) -> tuple:
		return (
			model.status==item.value.status,
			model.digest==item.value.data.digest.string,
			model.chain==item.value.chain,
			model.reserved==item.value.reserved
		)

	@pydantic.validate_arguments
	def save(self, item: Rows.Item) -> None:
		if self._model(item)(**self._row(item)).save(force_insert=True) != 1:
			raise Rows.OperationalError(item, 'save')

	def update(self, old: Rows.Item, new: Rows.Item) -> None:

		model = Model(self.db, old.value.type)

		if (
			model
			.update(**self._row(new))
			.where(self._where(model, old)).execute()
		) != 1:
			raise Rows.OperationalError(old, 'update')

	@pydantic.validate_arguments
	def unreserve(self, item: Rows.Item) -> None:
		model = Model(self.db, item.value.type)
		model.update(reserved=None).where(self._where(model, item)).execute()

	@pydantic.validate_arguments
	def delete(self, item: Rows.Item) -> None:
		model = Model(self.db, item.value.type)
		model.delete().where(self._where(model, item)).execute()