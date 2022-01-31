import sys
from loguru import logger
from peewee import Database
from datetime import datetime
from peewee import FixedCharField, DateTimeField

from .. import Item
from .. import Model, ItemRepositoryLogger



logger.configure(
	handlers=[
		{
			'sink': sys.stderr,
			'format': '{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{message}</level>'
		}
	],
)


class DefaultItemRepositoryLogger(ItemRepositoryLogger):

	def __init__(self, db: Database, log_table_name: str='conveyor_log'):

		self.db = db

		self.model = Model(db, log_table_name, {
			'date': DateTimeField(),
			'type': FixedCharField(max_length=63),
			'chain_id': FixedCharField(max_length=63),
			'worker': FixedCharField(max_length=63, null=True),
			'status_old': FixedCharField(max_length=63, null=True),
			'status_new': FixedCharField(max_length=63, null=True)
		})
		if not self.model.table_exists():
			db.create_tables([self.model])
	
	def _log_item(self, new_item: Item, old_item: Item=Item()) -> None:
		self.model(
			date=str(datetime.utcnow()),
			chain_id=new_item.chain_id or old_item.chain_id,
			worker=new_item.worker,
			type=new_item.type,
			status_old=old_item.status,
			status_new=new_item.status
		).save()

	def create(self, item):
		self._log_item(item)
		logger.info(f'-> {item.type}::{item.status}')
	
	def update(self, type, id, item):
		
		model = Model(self.db, type)
		if not model:
			return None

		item_row = model.select(model.status).where(model.id==id).get()
		self._log_item(
			new_item=item,
			old_item=Item(status=item_row.status)
		)
		
		logger.info(f'{type}::{item_row.status.rstrip()}::{id} -> {type}::{item.status}')

	def delete(self, type, id):

		model = Model(self.db, type)
		if not model:
			return None

		item_row = model.select(model.status, model.chain_id).where(model.id==id).get()
		self._log_item(
			new_item=Item(
				type=type,
				chain_id=item_row.chain_id
			),
			old_item=Item(
				status=item_row.status
			)
		)

		logger.info(f'{type}::{item_row.status.rstrip()}::{id} ->')