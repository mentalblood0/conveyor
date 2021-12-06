import shutil
from peewee import PostgresqlDatabase, CharField

from tests import config, XmlVerifier, Typer, FileSaver
from conveyor.input_providers import ItemInputProvider
from conveyor.output_providers import ItemOutputProvider



def test_example():

	shutil.rmtree('./dir_tree')

	db = PostgresqlDatabase(
		config.db['db'], 
		user=config.db['user'], 
		password=config.db['password'], 
		host=config.db['host'], 
		port=config.db['port']
	)

	item_providers_args = [
		db,
		'undefined',
		{
			'file_path': CharField()
		}
	]

	item_output_provider = ItemOutputProvider('./dir_tree', *item_providers_args)
	item_input_provider = ItemInputProvider(*item_providers_args)

	file_saver_creator = FileSaver(item_output_provider)
	with open('tests/example_file.xml', 'rb') as f:
		text = f.read()

	is_xml_transformer = XmlVerifier(item_input_provider)
	get_type_transformer = Typer(item_input_provider)

	item_input_provider.db_item_type_interface.drop()
	assert file_saver_creator(text)
	assert is_xml_transformer() == 'xml'
	assert get_type_transformer() == 'PersonalizationRequest'