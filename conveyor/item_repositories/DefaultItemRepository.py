import os
from typing import Union
from functools import cache
from growing_tree_base import *
from peewee import Model as Model_
from peewee import CharField, IntegerField, FloatField, DateTimeField

from .. import Command, Item, Repository, Model
from . import FileRepository, MetadataRepository



def getFields(item: Item) -> dict[str, Union[str, int, float]]:
	return {
		k: v
		for k, v in (item.metadata | item.__dict__).items()
		if not k in ['data', 'metadata', 'type', 'id']
	}


def installLoggingCommon(db, log_table_name='conveyor_log'):

	log_model = Model(db, log_table_name, {
		'date': DateTimeField(),
		'chain_id': CharField(),
		'worker': CharField(null=True),
		'type': CharField(),
		'status_old': CharField(null=True),
		'status_new': CharField(null=True)
	})
	if not log_model.table_exists():
		db.create_tables([log_model])

	db.execute_sql('''
		CREATE OR REPLACE FUNCTION conveyor_log_function()
			RETURNS trigger as $$
			BEGIN
				INSERT INTO conveyor_log (
					date,
					chain_id,
					worker,
					type,
					status_old,
					status_new
				)
				VALUES (
					NOW()::timestamp,
					GREATEST(OLD.chain_id, NEW.chain_id),
					NEW.worker,
					TG_TABLE_NAME,
					OLD.status,
					NEW.status
				);
				RETURN NEW;
			END;
			$$ LANGUAGE 'plpgsql';
		'''
	)


def installLoggingForTable(db, table_name):

	db.execute_sql(f'''
		CREATE OR REPLACE TRIGGER conveyor_log_trigger
			AFTER 
				INSERT OR 
				UPDATE OR 
				DELETE 
			ON {table_name}
			FOR EACH ROW
			EXECUTE PROCEDURE conveyor_log_function();
		'''
	)


@cache
def getModel(db: Model_, item: Item) -> Model_:

	columns = {
		k: {
			str: CharField(default=''),
			int: IntegerField(default=0),
			float: FloatField(default=0.0)
		}[type(v)]
		for k, v in getFields(item).items()
	}

	model = Model(db, item.type, columns)
	if not model.table_exists():
		db.create_tables([model])
		installLoggingCommon(db)
		installLoggingForTable(db, model.__name__)

	return model


class Create(Command):

	def execute(self, item: Item, dir_tree_root_path: str, metadata_repository: MetadataRepository=None, file_repository: FileRepository=None) -> int:

		item.metadata['file_path'] = file_repository.transaction().create(
			text=item.data,
			dir_tree_root_path=os.path.join(dir_tree_root_path, item.type)
		).execute()[0]

		metadata_repository.transaction().create(item).execute()
	
	def _revert(self, *args, **kwargs):
		pass


class Update(Command):

	def execute(self, type: str, id: str, item: Item, metadata_repository: MetadataRepository, *args, **kwargs) -> int:
		metadata_repository.transaction().update(type, id, item).execute()
	
	def _revert(self, *args, **kwargs):
		pass


class Delete(Command):

	def execute(self, type: str, id: str, metadata_repository: MetadataRepository, file_repository: FileRepository, *args, **kwargs) -> int:

		file_path = metadata_repository.getById(type, id)['file_path']

		metadata_repository.transaction().delete(type, id).execute()
		file_repository.transaction().delete(file_path).execute()
	
	def _revert(self, *args, **kwargs):
		pass


class Drop(Command):

	def execute(self, type: str, metadata_repository: MetadataRepository, *args, **kwargs) -> int:
		metadata_repository.transaction().drop(type).execute()
	
	def _revert(self, *args, **kwargs):
		pass


def get(type: str, status: str, limit: int, metadata_repository: MetadataRepository, file_repository: FileRepository, *args, **kwargs) -> Item:

	result = metadata_repository.get(type, status, limit)
	for i in result:
		i.data = file_repository.get(i.data)
	
	return result


class DefaultItemRepository(Repository):

	subrepositories = {
		'metadata': MetadataRepository.MetadataRepository,
		'file': FileRepository.FileRepository
	}

	commands = {
		'create': Create,
		'update': Update,
		'delete': Delete,
		'drop': Drop
	}

	queries = {
		'get': get
	}