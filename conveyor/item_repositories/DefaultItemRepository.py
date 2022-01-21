import os
from typing import Union
from growing_tree_base import *
from peewee import Model as Model_
from functools import lru_cache
from peewee import CharField, IntegerField, FloatField, DateTimeField

from .. import Command, Item, Repository, Model



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


def getFileContent(path: str) -> str:

	with open(path, 'r', encoding='utf8') as f:
		file_content = f.read()

	return file_content


class Create(Command):

	def execute(self, item: Item, db: Model_, dir_tree_root_path: str, base_file_name: str='.xml', *args, **kwargs) -> int:

		item.metadata['file_path'] = saveToDirTree(
			item.data, 
			os.path.join(dir_tree_root_path, item.type),
			base_file_name=base_file_name
		)

		model = getModel(db, item)
		instance = model(**getFields(item))
		instance.save()

		return instance.get_id()
	
	def _revert(self, item: Item, db: Model_, result: str, *args, **kwargs):

		try:
		
			model = Model(db, item.type)
			if not model:
				return None

			model.delete().where(model.id==result).execute()
		
		except Exception:
			pass

		try:
			os.remove(item.metadata['file_path'])
		except FileNotFoundError:
			pass


class Update(Command):

	def execute(self, type: str, id: str, item: Item, db: Model_, *args, **kwargs) -> int:

		model = Model(db, type)
		if not model:
			return None

		return model.update(**getFields(item)).where(model.id==id).execute()
	
	def _revert(self, *args, **kwargs):
		pass


class Delete(Command):

	def execute(self, type: str, id: str, db: Model_, *args, **kwargs) -> int:

		model = Model(db, type)
		if not model:
			return None

		file_path = model.select().where(model.id==id).get().__data__['file_path']

		result = model.delete().where(model.id==id).execute()

		try:
			os.remove(file_path)
		except FileNotFoundError:
			pass
		
		return result
	
	def _revert(self, *args, **kwargs):
		pass


class Drop(Command):

	def execute(self, type: str, db: Model_, *args, **kwargs) -> int:

		model = Model(db, type)
		if not model:
			return None
		
		return db.drop_tables([model])
	
	def _revert(self, *args, **kwargs):
		pass


def get(type: str, status: str, limit: int, db: Model_, getFileContentCached: None, *args, **kwargs) -> Item:

	model = Model(db, type)
	if not model:
		return []

	query_result = model.select().where(model.status==status).limit(limit)
	result = []

	for r in query_result:

		item_db_dict = r.__data__

		file_content = getFileContentCached(item_db_dict['file_path'])
	
		result.append(
			Item(
				id=item_db_dict['id'],
				type=type,
				status=status,
				data=file_content,
				chain_id=item_db_dict['chain_id'],
				metadata={
					k: v
					for k, v in item_db_dict.items()
					if not k in ['status', 'type', 'data', 'chain_id', 'id', 'worker']
				}
			)
		)
	
	return result


class DefaultItemRepository(Repository):

	commands = {
		'create': Create,
		'update': Update,
		'delete': Delete,
		'drop': Drop
	}

	queries = {
		'get': get
	}

	def __init__(self, *args, cache_size=2**10, **kwargs):

		kwargs |= {
			'getFileContentCached': lru_cache(maxsize=cache_size)(getFileContent)
		}

		super().__init__(*args, **kwargs)