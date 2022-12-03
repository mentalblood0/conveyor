import peewee
import pydantic
import dataclasses
from __future__ import annotations

from ...core import Item
from ...common.Model import Model, BaseModel, metadata_fields



@dataclasses.dataclass(frozen=True)
class ItemAdapter:

	item: Item
	db: peewee.Database

	class OperationalError(Exception):
		@pydantic.validate_arguments
		def __init__(self, item: Item, action: str):
			super().__init__(f'Item {action} (type={item.type}, status={item.status}, digest={item.data.digest.string}) had no result')

	def __post_init__(self):
		for k in self.item.metadata:
			if hasattr(self.item, k):
				raise KeyError(f'Field name "{k}" reserved and can not be used in metadata')

	@property
	def fields(self) -> dict[str, Item.Value]:
		return {
			'status': self.item.status,
			'chain': self.item.chain.value
		} | self.item.metadata

	@property
	def model(self) -> type[BaseModel]:
		return Model(
			db=self.db,
			name=self.item.type,
			metadata_columns={
				k: metadata_fields[type(v)]()
				for k, v in self.item.metadata.items()
			}
		)

	def save(self) -> None:
		if self.model(**self.fields).save(force_insert=True) != 1:
			raise ItemAdapter.OperationalError(self.item, 'save')

	@pydantic.validate_arguments
	def update(self, new: ItemAdapter) -> None:

		model = Model(self.db, self.item.type)

		if (
			model
			.update(**new.fields)
			.where(
				model.status==self.item.status,
				model.digest==self.item.data.digest.string,
				model.chain==self.item.chain,
				model.reserved==self.item.reserved
			).execute()
		) != 1:
			raise ItemAdapter.OperationalError(self.item, 'update')

	def unreserve(self) -> None:

		model = Model(self.db, self.item.type)

		model.update(reserved=None).where(
			model.status==self.item.status,
			model.digest==self.item.data.digest.string,
			model.chain==self.item.chain,
			model.reserved==self.item.reserved
		).execute()

	def delete(self) -> None:

		model = Model(self.db, self.item.type)

		model.delete().where(
			model.status==self.item.status,
			model.digest==self.item.data.digest.string,
			model.chain==self.item.chain,
			model.reserved==self.item.reserved
		)