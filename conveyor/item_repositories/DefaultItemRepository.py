import os
import base64
from typing import Union
from blake3 import blake3
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


def getFileContent(path: str) -> bytes:

	with open(path, 'rb') as f:
		file_content = f.read()

	return file_content


def getDataDigest(data: bytes | str):
	
	data = data if type(data) == bytes else data.encode('utf8')
	
	d = blake3(data).digest()
	return base64.b64encode(d).decode('ascii')


class Create(Command):

	def execute(self, item: Item, db: Model_, dir_tree_root_path: str, base_file_name: str='.xml', *args, **kwargs) -> int:

		item.metadata |= {
			'file_path': saveToDirTree(
				item.data,
				os.path.join(dir_tree_root_path, item.type),
				base_file_name=base_file_name
			),
			'data_digest': getDataDigest(item.data)
		}

		model = getModel(db, item)
		instance = model(**getFields(item))
		instance.save()
	
	def _revert(self, item: Item, *args, **kwargs):
		os.remove(item.metadata['file_path'])


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

		data = getFileContentCached(item_db_dict['file_path'])
		if getDataDigest(data) != item_db_dict['data_digest']:
			item_info = {
				'type': type,
				'status': status,
				'chain_id': item_db_dict['chain_id']
			}
			raise Exception(f"Error geting item {item_info}: data corrupted")

		item = Item(
			id=item_db_dict['id'],
			type=type,
			status=status,
			data=data.decode('utf8'),
			chain_id=item_db_dict['chain_id']
		)
		item.metadata = {
			k: v
			for k, v in item_db_dict.items()
			if not k in [*item.__dict__.keys()] + ['worker', 'data_digest']
		}

		result.append(item)
	
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