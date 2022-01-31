import os
import growing_tree_base
from datetime import datetime
from functools import lru_cache
from dataclasses import dataclass
from peewee import Database, Model as Model_
from peewee import CharField, FixedCharField, IntegerField, FloatField, DateTimeField

from .. import Item, ItemRepository, Model, ItemRepositoryLogger



class DefaultItemRepositoryLogger(ItemRepositoryLogger):

	def __init__(self, db, log_table_name='conveyor_log'):

		self.model = Model(db, log_table_name, {
			'date': DateTimeField(),
			'chain_id': FixedCharField(max_length=63),
			'worker': FixedCharField(max_length=63, null=True),
			'type': FixedCharField(max_length=63),
			'status': FixedCharField(max_length=63, null=True)
		})
		if not self.model.table_exists():
			db.create_tables([self.model])
	
	def _log_item(self, item):
		self.model(
			date=str(datetime.utcnow()),
			chain_id=item.chain_id,
			worker=item.worker,
			type=item.type,
			status=item.status
		).save()

	def create(self, item):
		self._log_item(item)
	
	def update(self, type, id, item):
		self._log_item(item)

	def delete(self, type, id):
		return