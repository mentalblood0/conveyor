import pydantic
from datetime import datetime
from peewee import Database, SqliteDatabase, PostgresqlDatabase, CharField, DateTimeField, IntegerField

from ...core import Item
from ...common import Model



class ItemId(int):

	@pydantic.validate_arguments
	def __new__(C, value: str | int):

		if type(value) == int:
			return super().__new__(C, value)

		elif type(value) == str:
			if not len(value):
				result_value = -1
			else:
				result_value = int(value)
			return super().__new__(C, result_value)


class ExceptionLogsRepository:

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __init__(self, db: Database, name: str='conveyor_errors') -> None:

		self.db = db
		self.columns = {
			'date': DateTimeField(index=True),
			'worker_name': CharField(max_length=63, index=True),
			'item_type': CharField(max_length=63, null=True, index=True),
			'item_status': CharField(max_length=63, null=True, index=True),
			'item_chain_id': CharField(max_length=63, null=True, index=True),
			'item_id': IntegerField(null=True, index=True),
			'error_type': CharField(max_length=63),
			'error_text': CharField(max_length=255)
		}
		self.uniques = [(
			'worker_name',
			'item_chain_id',
			'item_id',
			'error_type',
			'error_text'
		)]
		self.exceptions = Model(self.db, name, self.columns, self.uniques)
	
	def _handleConflict(self, query, row):

		if type(self.db) in [PostgresqlDatabase, SqliteDatabase]:
			return query.on_conflict(
				conflict_target=tuple(
					getattr(self.exceptions, name)
					for name in self.uniques[0]
				),
				update={
					self.exceptions.date: row['date']
				}
			)

		else:
			return query.on_conflict('replace')

	@pydantic.validate_arguments
	def create(self, item: Item, exception_type: str, exception_text: str, worker_name: str) -> int:

		row = {
			'date': str(datetime.utcnow()),
			'worker_name': worker_name,
			'item_type': item.type,
			'item_status': item.status,
			'item_chain_id': item.chain_id,
			'item_id': ItemId(item.id),
			'error_type': exception_type,
			'error_text': exception_text[:255]
		}

		query = self.exceptions.insert(**row)

		return self._handleConflict(query, row).execute()

	def delete(self, item: Item, worker_name: str) -> int:

		return self.exceptions.delete().where(
			self.exceptions.worker_name==worker_name,
			self.exceptions.item_type==item.type,
			self.exceptions.item_status==item.status,
			self.exceptions.item_chain_id==item.chain_id,
			self.exceptions.item_id==ItemId(item.id)
		).execute()