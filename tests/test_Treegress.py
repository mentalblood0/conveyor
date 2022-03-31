import shutil

from conveyor import Item

from .common import *



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
	assert repository.get(type, {'status': status}, limit=None)[0].metadata['message_id'] == item.metadata['message_id']

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
	id = repository.get(type, {'status': status})[0].id
	assert repository.delete(type, id)
	assert repository.get(type, {'status': status}) == []

	clear()