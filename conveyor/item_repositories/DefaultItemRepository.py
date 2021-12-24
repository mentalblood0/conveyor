import os
from growing_tree_base import *
from functools import cache, lru_cache
from rollbackable import Rollbackable
from peewee import CharField, IntegerField, FloatField

from .. import Item, ItemRepository, Model



def getFields(item):
	return {
		k: v
		for k, v in (item.metadata | item.__dict__).items()
		if not k in ['data', 'metadata', 'type', 'id']
	}


@cache
def getModel(db, item):

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

	return model


def getFileContent(path):

	with open(path, 'r', encoding='utf8') as f:
		file_content = f.read()

	return file_content


class DefaultItemRepository(ItemRepository):

	def __init__(self, db, dir_tree_root_path, cache_max_size=1024):
		self.db = db
		self.dir_tree_root_path = dir_tree_root_path
		self.getFileContent = lru_cache(maxsize=cache_max_size)(getFileContent)

	def create(self, item):

		item.metadata['file_path'] = saveToDirTreeRollbackable(
			item.data, 
			os.path.join(self.dir_tree_root_path, item.type),
			base_file_name='.xml'
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

			file_content = self.getFileContent(item_db_dict['file_path'])
		
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
						if not k in ['status', 'type', 'data', 'chain_id', 'id']
					}
				)
			)
		
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
	def atomic(self):

		def decorator(f):
			def new_f(*args, **kwargs):
				with Rollbackable(saveToDirTree, os.remove) as saveToDirTreeRollbackable:
					# f.__globals__['saveToDirTreeRollbackable'] = saveToDirTreeRollbackable
					print('with')
					with self.db.atomic():
						result = f(*args, **kwargs)
				return result
			return new_f

		return decorator
	
	def _drop(self, type):

		model = Model(self.db, type)
		if not model:
			return None
		
		return self.db.drop_tables([model])