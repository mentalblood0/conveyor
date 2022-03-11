from dataclasses import dataclass

from .. import Item
from .. import RepositoryEffect
from ..Repository import Repository
from ..LogsRepository import LogsRepository



@dataclass
class DbLogging(RepositoryEffect):

	repository: Repository
	logs_repository: LogsRepository

	def create(self, item):
		self.logs_repository.create('create', item)
	
	def update(self, type, id, item):

		print('log update')

		old_item = self.repository.get(type, id)

		self.logs_repository.create(
			action='update',
			new_item=item,
			old_item=old_item
		)

	def delete(self, type, id):

		old_item = self.repository.get(type, id)

		self.logs_repository.create(
			action='delete',
			new_item=Item(
				type=type,
				chain_id=old_item.chain_id
			),
			old_item=Item(
				status=old_item.status
			)
		)