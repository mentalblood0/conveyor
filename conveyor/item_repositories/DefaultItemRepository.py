import os
import lzma
import base64
from typing import Union
from blake3 import blake3
from growing_tree_base import *
from functools import lru_cache
from peewee import CharField, IntegerField, FloatField, DateTimeField, Model as Model_

from .. import Item, ItemRepository, Model



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


def getFields(item: Item) -> dict[str, Union[str, int, float]]:
	return {
		k: v
		for k, v in (item.metadata | item.__dict__).items()
		if not k in ['data', 'metadata', 'type', 'id']
	}


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


def getDigest(data: bytes) -> str:
	d = blake3(data, max_threads=blake3.AUTO).digest()
	return base64.b64encode(d).decode('ascii')


def getFileContent(path: str, digest: str) -> str:

	with lzma.open(path) as f:
		file_content = f.read()
	
	correct_digest = getDigest(file_content)
	if correct_digest != digest:
		raise Exception(f"Cannot get file content: digest invalid: '{digest}' != '{correct_digest}'")

	return file_content.decode()


class DefaultItemRepository(ItemRepository):

	def __init__(self, db, dir_tree_root_path, base_file_name='.xz', cache_size=1024):
		self.db = db
		self.base_file_name = base_file_name
		self.dir_tree_root_path = dir_tree_root_path
		self.getFileContent = lru_cache(maxsize=cache_size)(getFileContent)

	def create(self, item):

		item_data_bytes = item.data.encode('utf8')
		item.data_digest = getDigest(item_data_bytes)

		item.metadata['file_path'] = saveToDirTree(
			file_content=lzma.compress(item_data_bytes, filters=[
				{"id": lzma.FILTER_LZMA2, "preset": lzma.PRESET_EXTREME},
			]), 
			root_dir=os.path.join(self.dir_tree_root_path, item.type),
			base_file_name=self.base_file_name
		)

		return getModel(self.db, item)(**getFields(item)).save()

	def get(self, type, status, limit=None):

		model = Model(self.db, type)
		if not model:
			return []

		query_result = model.select().where(model.status==status).limit(limit)
		result = []

		for r in query_result:

			item_db_dict = r.__data__

			item = Item(
				type=type,
				status=status,
				id=item_db_dict['id'],
				chain_id=item_db_dict['chain_id'],
				data_digest = item_db_dict['data_digest'],
				data=self.getFileContent(item_db_dict['file_path'], item_db_dict['data_digest'])
			)
			item.metadata = {
				k: v
				for k, v in item_db_dict.items()
				if not k in [*item.__dict__.keys()] + ['worker', 'data_digest']
			}

			result.append(item)
		
		return result
	
	def update(self, type, id, item):

		model = Model(self.db, type)
		if not model:
			return None

		return model.update(**getFields(item)).where(model.id==id).execute()

	def delete(self, type, id):

		model = Model(self.db, type)
		if not model:
			return None

		file_path = model.select().where(model.id==id).get().__data__['file_path']

		result = model.delete().where(model.id==id).execute()

		try:
			os.remove(file_path)
		except FileNotFoundError:
			pass
		
		return result

	@property
	def transaction(self):

		def decorator(f):
			def new_f(*args, **kwargs):
				with self.db.transaction():
					result = f(*args, **kwargs)
				return result
			return new_f

		return decorator
	
	def _drop(self, type):

		model = Model(self.db, type)
		if not model:
			return None
		
		return self.db.drop_tables([model])
