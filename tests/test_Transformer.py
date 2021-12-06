from peewee import PostgresqlDatabase, CharField

from tests import config, isXml
from conveyor.input_providers import ItemInputProvider



def test_example():

	db = PostgresqlDatabase(
		config.db['db'], 
		user=config.db['user'], 
		password=config.db['password'], 
		host=config.db['host'], 
		port=config.db['port']
	)

	item_input_provider = ItemInputProvider(
		db, 
		'PersonalizationRequest', 
		{
			'message_id': CharField(),
			'file_path': CharField()
		}
	)

	item_input_provider.db_item_type_interface.drop()
	item_input_provider.db_item_type_interface.add({
		'message_id': 'lalala',
		'file_path': 'tests/example_file.xml'
	})

	is_xml_transformer = isXml(item_input_provider)
	new_status = is_xml_transformer()

	assert new_status == 'xml'