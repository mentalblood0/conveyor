from conveyor import DbItemTypeInterface
from peewee import PostgresqlDatabase, CharField

from . import config


db = PostgresqlDatabase(
	config.db['db'], 
	user=config.db['user'], 
	password=config.db['password'], 
	host=config.db['host'], 
	port=config.db['port']
)
items = DbItemTypeInterface(db, 'PersonalizationRequest', {'message_id': CharField()})


def test_drop():

	items.drop()
	assert not items.item_type.table_exists()


def test_create():

	items.drop()
	items.create()
	assert items.item_type.table_exists()


def test_add():

	items.drop()
	items.add({
		'message_id': 'lalala'
	})
	assert items.get('created') == {
		'id': 1,
		'status': 'created',
		'message_id': 'lalala'
	}


def test_set():

	items.drop()
	items.add({
		'message_id': 'lalala'
	})
	
	id = items.get('created')['id']
	items.setStatus(id, 'checked')
	assert items.get('checked')['status'] != None


def test_delete():

	items.drop()
	items.add({
		'message_id': 'lalala'
	})

	id = items.get('created')['id']
	items.delete(id)
	assert items.get('created') == None