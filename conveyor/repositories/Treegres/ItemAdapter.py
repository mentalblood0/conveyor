import dataclasses
from typing import Callable
from functools import partial
from datetime import datetime
from peewee import Field, CharField, IntegerField, FloatField, DateTimeField, Database

from ...core import Item
from ...common import Model

from . import Path



base_fields_mapping: dict[str, Callable[[], Field]] = {
	'chain_id': partial(CharField, max_length=63, index=True),
	'status': partial(CharField, max_length=63, index=True),
	'data_digest': partial(CharField, max_length=63),
	'reserved_by': partial(CharField, default=None, null=True, index=True, max_length=31),
	'date_created': partial(DateTimeField, default=None, null=True, index=True)
}

metadata_fields_mapping: dict[type, Callable[[], Field]] = {
	str: partial(CharField, default=None, null=True, index=True),
	int: partial(IntegerField, default=None, null=True, index=True),
	float: partial(FloatField, default=None, null=True, index=True),
	datetime: partial(DateTimeField, default=None, null=True, index=True),
	Path: partial(CharField, index=True)
}


@dataclasses.dataclass(frozen=True)
class ItemAdapter:

	item: Item
	db: Database

	def __post_init__(self):

		for k in self.item.metadata:
			if hasattr(self.item, k):
				raise KeyError(f'Field name "{k}" reserved and can not be used in metadata')

		object.__setattr__(
			self,
			'item',
			dataclasses.replace(
				self.item,
				reserved_by=None
			)
		)

	@property
	def fields(self):
		return {
			k: v if type(v) != type else None
			for k, v in self.item.metadata.items()
		} | {
			k: getattr(self.item, k)
			for k in base_fields_mapping
		}

	@property
	def model(self):
		return Model(
			db=self.db,
			name=self.item.type,
			columns={
				k: metadata_fields_mapping[type(v) if type(v) != type else v]()
				for k, v in self.item.metadata.items()
			} | {
				k: base_fields_mapping[k]()
				for k in base_fields_mapping
			}
		)

	def save(self):
		return self.model(**self.fields).save(force_insert=True)
	
	def update(self):

		if not (model := Model(self.db, self.item.type)):
			return None

		return model.update(
			**{
				k: v
				for k, v in self.fields.items()
				if k not in ['file_path', 'date_created']
			}
		).where(model.id==self.item.id).execute()