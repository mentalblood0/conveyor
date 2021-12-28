import os
from functools import cache
from growing_tree_base import *
from peewee import CharField, IntegerField, FloatField

from .. import Command, Item, ItemRepository, Model



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


class create(Command):

	def __call__(self, item, db, dir_tree_root_path):

		item.metadata['file_path'] = saveToDirTree(
				item.data, 
				os.path.join(dir_tree_root_path, item.type),
				base_file_name='.xml'
			)

		return getModel(db, item)(**getFields(item)).save()
	
	def revert(self):
		pass


class update(Command):

	def __call__(self, type, id, item, db, dir_tree_root_path):

		model = Model(db, type)
		if not model:
			return None

		return model.update(**getFields(item)).where(model.id==id).execute()
	
	def revert(self):
		pass


class delete(Command):

	def __call__(type, id, db, dir_tree_root_path):

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
	
	def revert(self):
		pass


class drop(Command):

	def __call__(type, db, dir_tree_root_path):

		model = Model(db, type)
		if not model:
			return None
		
		return db.drop_tables([model])
	
	def revert(self):
		pass


class DefaultItemRepository(ItemRepository):

	commands = {
		'create': create,
		'update': update,
		'delete': delete,
		'drop': drop
	}

	def get(self, type, status, limit):

		model = Model(self.db, type)
		if not model:
			return []

		query_result = model.select().where(model.status==status).limit(limit)
		result = []

		for r in query_result:

			item_db_dict = r.__data__

			file_content = getFileContent(item_db_dict['file_path'])
		
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