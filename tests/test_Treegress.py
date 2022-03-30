import shutil
from peewee import SqliteDatabase

from conveyor import Item
from conveyor.repositories import Treegres



db = SqliteDatabase(':memory:')
dir_tree_root_path = 'dir_tree'
repository = Treegres(db=db, dir_tree_root_path=dir_tree_root_path)

type = 'undefined'
status = 'created'


def clear():
	repository._drop(type)
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)


def test_create():

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

	clear()


def test_get():

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

	clear()


def test_delete():

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

	clear()