from dataclasses import dataclass

from ...core import Repository, Effect
from .LogsRepository import LogsRepository



@dataclass
class DbLogging(Effect):

	repository: Repository
	logs_repository: LogsRepository

	def create(self, item):
		self.logs_repository.create(
			action='create',
			new_item=item
		)
	
	def update(self, item):
		self.logs_repository.create(
			action='update',
			old_item=self.repository.get(item.type, {'id': item.id}, ['status'])[0],
			new_item=item
		)

	def delete(self, type, id):
		self.logs_repository.create(
			action='delete',
			old_item=self.repository.get(type, {'id': id}, ['status', 'chain_id'])[0]
		)