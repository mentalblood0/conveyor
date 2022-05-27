import pydantic
from dataclasses import dataclass

from .LogsRepository import LogsRepository
from ...core import Repository, Effect, Item



@dataclass
class DbLogging(Effect):

	repository: Repository
	logs_repository: LogsRepository

	@pydantic.validate_arguments
	def create(self, item: Item):
		self.logs_repository.create(
			action='create',
			new_item=item
		)

	@pydantic.validate_arguments
	def update(self, item: Item):
		self.logs_repository.create(
			action='update',
			old_item=self.repository.get(item.type, {'id': item.id}, ['status'])[0],
			new_item=item
		)

	@pydantic.validate_arguments
	def delete(self, type: str, id: str | int):
		self.logs_repository.create(
			action='delete',
			old_item=self.repository.get(type, {'id': id}, ['status', 'chain_id'])[0]
		)