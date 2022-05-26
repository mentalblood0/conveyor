from datetime import datetime
from peewee import Database, CharField, DateTimeField

from ...core import Item
from ...common import Model



class ExceptionLogsRepository:

	def __init__(self, db: Database, name='conveyor_errors') -> None:

		self.db = db
		self.exceptions = Model(db, name, {
			'date': DateTimeField(index=True),
			'worker_name': CharField(max_length=63, index=True),
			'item_type': CharField(max_length=63, index=True),
			'item_status': CharField(max_length=63, index=True),
			'item_chain_id': CharField(max_length=63, index=True),
			'error_type': CharField(max_length=63),
			'error_text': CharField(max_length=255)
		})
	
	def create(self, item: Item, exception_type: str, exception_text: str, worker_name: str) -> None:
		self.exceptions(
			date=str(datetime.utcnow()),
			worker_name=worker_name,
			item_type=item.type,
			item_status=item.status,
			item_chain_id=item.chain_id,
			error_type=exception_type,
			error_text=exception_text[:255]
		).save()