from peewee import Database
from datetime import datetime
from peewee import FixedCharField, DateTimeField

from .. import Item
from .. import Model, ItemRepositoryLogger



class DefaultItemRepositoryLogger(ItemRepositoryLogger):

	def __init__(self, db: Database, log_table_name: str='conveyor_log'):

		self.model = Model(db, log_table_name, {
			'date': DateTimeField(),
			'type': FixedCharField(max_length=63),
			'chain_id': FixedCharField(max_length=63),
			'worker': FixedCharField(max_length=63, null=True),
			'status': FixedCharField(max_length=63, null=True)
		})
		if not self.model.table_exists():
			db.create_tables([self.model])
	
	def _log_item(self, item: Item) -> None:
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