import shutil
from peewee import SqliteDatabase

from conveyor import Item
from conveyor.repositories import Treegres



db = SqliteDatabase('test.db')
dir_tree_root_path = 'dir_tree'
repository = Treegres(db=db, dir_tree_root_path=dir_tree_root_path)


def clear(type):
	repository._drop(type)
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

def test_create():

	type = 'undefined'
	clear(type)

	item = Item(
		type=type,
		status='created',
		chain_id='ideeee',
		data='lalala',
		data_digest='lololo',
		metadata={
			'message_id': 'lololo'
		}
	)

	assert repository.create(item)


def test_get():

	type = 'undefined'
	status = 'created'
	clear(type)

	item = Item(
		type=type,
		status=status,
		chain_id='ideeee',
		data='lalala',
		data_digest='lololo',
		metadata={
			'message_id': 'lololo'
		}
	)

	assert repository.create(item)
	assert repository.fetch(type, status, None)[0].metadata['message_id'] == item.metadata['message_id']


def test_delete():

	type = 'undefined'
	status = 'created'
	clear(type)

	assert repository.create(Item(
		type=type,
		status=status,
		chain_id='ideeee',
		data='lalala',
		data_digest='lololo',
		metadata={
			'message_id': 'lololo'
		}
	))
	id = repository.fetch(type, status, 1)[0].id
	assert repository.delete(type, id)
	assert repository.fetch(type, status, None) == []