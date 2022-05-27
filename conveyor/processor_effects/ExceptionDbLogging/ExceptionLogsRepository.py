from datetime import datetime
from peewee import Database, CharField, DateTimeField, IntegerField

from ...core import Item
from ...common import Model



class ExceptionLogsRepository:

	def __init__(self, db: Database, name='conveyor_errors') -> None:

		self.db = db
		self.exceptions = Model(db, name, columns={
			'date': DateTimeField(index=True),
			'worker_name': CharField(max_length=63, index=True),
			'item_type': CharField(max_length=63, null=True, index=True),
			'item_status': CharField(max_length=63, null=True, index=True),
			'item_chain_id': CharField(max_length=63, null=True, index=True),
			'item_id': IntegerField(null=True, index=True),
			'error_type': CharField(max_length=63),
			'error_text': CharField(max_length=255)
		}, uniques=[(
			'worker_name',
			'item_chain_id',
			'item_id',
			'error_type',
			'error_text'
		)])
	
	def create(self, item: Item, exception_type: str, exception_text: str, worker_name: str) -> None:

		if not len(item.id):
			item_id = -1
		else:
			item_id = int(item.id)

		self.exceptions.insert(
			date=str(datetime.utcnow()),
			worker_name=worker_name,
			item_type=item.type,
			item_status=item.status,
			item_chain_id=item.chain_id,
			item_id=item_id,
			error_type=exception_type,
			error_text=exception_text[:255]
		).on_conflict('replace').execute()