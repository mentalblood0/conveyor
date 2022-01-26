import shutil
from peewee import PostgresqlDatabase
from conveyor import Item
from conveyor.item_repositories import DefaultItemRepository

from . import config



db = PostgresqlDatabase(
	config.db['db'], 
	user=config.db['user'], 
	password=config.db['password'], 
	host=config.db['host'], 
	port=config.db['port']
)
dir_tree_root_path = 'dir_tree'
repository = DefaultItemRepository(
	db=db,
	dir_tree_root_path=dir_tree_root_path
)


def test_create():

	type = 'undefined'

	repository._drop(type)
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	item = Item(
		type=type,
		status='created',
		data='lalala',
		metadata={
			'message_id': 'lololo'
		}
	)

	assert repository.create(item)


def test_get():

	type = 'undefined'
	status = 'created'

	repository._drop(type)
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	item = Item(
		type=type,
		status=status,
		data='lalala',
		metadata={
			'message_id': 'lololo'
		}
	)

	assert repository.create(item)
	assert repository.get(type, status, None)[0].metadata['message_id'] == item.metadata['message_id']


def test_delete():

	type = 'undefined'
	status = 'created'

	repository._drop(type)
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	assert repository.create(Item(
		type=type,
		status=status,
		data='lalala',
		metadata={
			'message_id': 'lololo'
		}
	))
	id = repository.get(type, status, 1)[0].id
	assert repository.delete(type, id)
	assert repository.get(type, status, None) == []