import pydantic
from datetime import datetime
from peewee import Database, SqliteDatabase, PostgresqlDatabase, CharField, DateTimeField, IntegerField, ModelInsert

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
			'date_first': DateTimeField(index=True),
			'date_last': DateTimeField(index=True),
			'count': IntegerField(default=1),
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

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def _handleConflict(self, query: ModelInsert) -> ModelInsert:

		if type(self.db) in [PostgresqlDatabase, SqliteDatabase]:
			return query.on_conflict(
				conflict_target=self.uniques[0],
				preserve='date_last',
				update={self.exceptions.count: self.exceptions.count + 1}
			)

		else:
			raise NotImplementedError(f'No conflict handling strategy for database {self.db}')

	@pydantic.validate_arguments
	def create(self, item: Item, exception_type: str, exception_text: str, worker_name: str) -> int:

		date = str(datetime.utcnow())

		return self._handleConflict(
			self.exceptions.insert(
				date_first=date,
				date_last=date,
				worker_name=worker_name,
				item_type=item.type,
				item_status=item.status,
				item_chain_id=item.chain_id,
				item_id=ItemId(item.id),
				error_type=exception_type,
				error_text=exception_text[:255]
			)
		).execute()

	@pydantic.validate_arguments
	def delete(self, item: Item, worker_name: str) -> int:

		return self.exceptions.delete().where(
			self.exceptions.item_type==item.type,
			self.exceptions.item_status==item.status,
			self.exceptions.item_chain_id==item.chain_id,
			self.exceptions.item_id==ItemId(item.id)
		).execute()