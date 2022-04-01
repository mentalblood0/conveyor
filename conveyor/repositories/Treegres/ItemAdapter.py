from typing import Callable
from functools import partial
from dataclasses import dataclass, asdict
from peewee import Field, CharField, IntegerField, FloatField, Database

from ...core import Item
from ...common import Model

from . import Path



base_fields_mapping: dict[str, Callable[[], Field]] = {
	'chain_id': partial(CharField, max_length=63, index=True),
	'status': partial(CharField, max_length=63, index=True),
	'data_digest': partial(CharField, max_length=63)
}

metadata_fields_mapping: dict[type, Callable[[], Field]] = {
	str: partial(CharField, default=None, null=True, index=True),
	int: partial(IntegerField, default=None, null=True, index=True),
	float: partial(FloatField, default=None, null=True, index=True),
	Path: partial(CharField, max_length=63, index=True)
}


@dataclass
class ItemAdapter:

	item: Item
	db: Database

	@property
	def fields(self):
		return self.item.metadata | {
			k: getattr(self.item, k)
			for k in base_fields_mapping
		}

	def save(self):
		return Model(
			db=self.db,
			name=self.item.type,
			columns={
				k: metadata_fields_mapping[type(v)]()
				for k, v in self.item.metadata.items()
			} | {
				k: base_fields_mapping[k]()
				for k in base_fields_mapping
			}
		)(**self.fields).save()
	
	def update(self):

		model = Model(self.db, self.item.type)
		if not model:
			return None

		return model.update(**self.fields).where(model.id==self.item.id).execute()