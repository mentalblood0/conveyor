import pydantic
from datetime import datetime
from peewee import Database, CharField, DateTimeField

from ...core import Item
from ...common import Model



class LogsRepository:

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __init__(self, db: Database, name='conveyor_log') -> None:
		
		self.db = db
		self.log = Model(db, name, {
			'date': DateTimeField(index=True),
			'type': CharField(max_length=63, index=True),
			'chain_id': CharField(max_length=63, index=True),
			'action': CharField(max_length=8, index=True),
			'status_old': CharField(max_length=63, null=True),
			'status_new': CharField(max_length=63, null=True, index=True)
		})

	@pydantic.validate_arguments
	def create(self, action: str, old_item: Item=Item(), new_item: Item=Item()) -> int:
		return self.log(
			date=str(datetime.utcnow()),
			chain_id=new_item.chain_id or old_item.chain_id,
			action=action,
			type=new_item.type or old_item.type,
			status_old=old_item.status or None,
			status_new=new_item.status or None
		).save()