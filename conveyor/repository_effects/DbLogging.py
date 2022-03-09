from peewee import Database
from dataclasses import dataclass

from .. import Item
from .. import Model, RepositoryEffect
from ..LogsRepository import LogsRepository



@dataclass
class DbLogging(RepositoryEffect):

	db: Database
	logs_repository: LogsRepository

	def create(self, item):
		self.logs_repository.create('create', item)
	
	def update(self, type, id, item):
		
		model = Model(self.db, type)
		if not model:
			return None

		item_row = model.select(model.status).where(model.id==id).get()
		self.logs_repository.create(
			action='update',
			new_item=item,
			old_item=Item(status=item_row.status)
		)

	def delete(self, type, id):

		model = Model(self.db, type)
		if not model:
			return None

		item_row = model.select(model.status, model.chain_id).where(model.id==id).get()
		self.logs_repository.create(
			action='delete',
			new_item=Item(
				type=type,
				chain_id=item_row.chain_id
			),
			old_item=Item(
				status=item_row.status
			)
		)