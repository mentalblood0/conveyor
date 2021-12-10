import os
from functools import cache
from growing_tree_base import *
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


class DefaultItemRepository(ItemRepository):

	def __init__(self, db, dir_tree_root_path):
		self.db = db
		self.dir_tree_root_path = dir_tree_root_path

	def save(self, item):

		print('save', item.type)

		item.metadata['file_path'] = saveToDirTree(
			item.data, 
			os.path.join(self.dir_tree_root_path, item.type),
			base_file_name='.xml'
		)

		return getModel(self.db, item)(**getFields(item)).save()

	def get(self, type, status):

		model = Model(self.db, type)
		if not model:
			return None

		query_result = model.select().where(model.status==status).first()
		if not query_result:
			return None
		item_db_dict = query_result.__data__

		file_path = item_db_dict['file_path']
		with open(file_path, 'r', encoding='utf8') as f:
			file_content = f.read()
		
		return Item(
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
	
	def set(self, type, id, item):

		model = Model(self.db, type)
		if not model:
			return None

		return model.update(**getFields(item)).where(model.id==id).execute()

	def delete(self, type, id):
		
		model = Model(self.db, type)
		if not model:
			return None
		
		return model.delete().where(model.id==id).execute()
	
	def deleteAll(self, type):

		model = Model(self.db, type)
		if not model:
			return None
		
		return model.delete().execute()
	
	def drop(self, type):

		model = Model(self.db, type)
		if not model:
			return None
		
		return self.db.drop_tables([model])



import sys
sys.modules[__name__] = DefaultItemRepository