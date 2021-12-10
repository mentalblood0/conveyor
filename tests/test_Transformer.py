import shutil
from peewee import PostgresqlDatabase, CharField

from conveyor.workers.factories import DestroyerFactory
from conveyor.providers import ItemInputProvider, ItemOutputProvider
from tests import config, XmlVerifier, Typer, FileSaver, PersonalizationRequestToCreatedMover



def test_example():

	shutil.rmtree('./dir_tree', ignore_errors=True)

	db = PostgresqlDatabase(
		config.db['db'], 
		user=config.db['user'], 
		password=config.db['password'], 
		host=config.db['host'], 
		port=config.db['port']
	)

	undefined_item_providers_args = [
		db,
		'undefined',
		{
			'file_path': CharField(),
			'message_id': CharField(default='')
		}
	]

	undefined_item_output_provider = ItemOutputProvider('./dir_tree/undefined', *undefined_item_providers_args)
	undefined_item_input_provider = ItemInputProvider(*undefined_item_providers_args)

	personalization_request_item_output_provider = ItemOutputProvider(
		'./dir_tree/PersonalizationRequest', 
		db, 
		'PersonalizationRequest', 
		{
			'file_path': CharField(),
			'message_id': CharField()
		}
	)

	file_saver_creator = FileSaver(undefined_item_output_provider)
	with open('tests/example_file.xml', 'rb') as f:
		text = f.read()

	is_xml_transformer = XmlVerifier(undefined_item_input_provider)
	get_type_transformer = Typer(undefined_item_input_provider)
	undefined_to_personalization_request_mover = PersonalizationRequestToCreatedMover(
		undefined_item_input_provider,
		personalization_request_item_output_provider
	)
	undefined_destroyer = DestroyerFactory('end')(undefined_item_input_provider)

	undefined_item_input_provider.db_item_type_interface.drop()
	personalization_request_item_output_provider.db_item_type_interface.drop()
	assert file_saver_creator(text)
	assert is_xml_transformer() == 'xml'
	assert get_type_transformer() == 'PersonalizationRequest'
	assert undefined_to_personalization_request_mover()
	assert undefined_destroyer()

	assert is_xml_transformer() == None
	assert get_type_transformer() == None

	assert file_saver_creator(text)
	assert is_xml_transformer() == 'xml'
	assert get_type_transformer() == 'PersonalizationRequest'
	assert undefined_to_personalization_request_mover()
	assert undefined_destroyer()

	shutil.rmtree('./dir_tree')