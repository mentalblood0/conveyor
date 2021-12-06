from peewee import PostgresqlDatabase, CharField

import isXml
from tests import config
from conveyor.input_providers import ItemInputProvider



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
		'message_id': CharField()
	}
)

is_xml_transformer = isXml(item_input_provider)
is_xml_transformer()