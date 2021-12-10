import shutil
from peewee import PostgresqlDatabase

from tests import config
from tests.example_workers import *
from conveyor.workers.factories import DestroyerFactory
from conveyor.item_repositories import DefaultItemRepository



db = PostgresqlDatabase(
	config.db['db'], 
	user=config.db['user'], 
	password=config.db['password'], 
	host=config.db['host'], 
	port=config.db['port']
)
repository = DefaultItemRepository(db, 'dir_tree')


def test_example():

	repository.drop('undefined')
	repository.drop('PersonalizationRequest')

	shutil.rmtree('dir_tree', ignore_errors=True)

	file_saver = FileSaver(repository)
	xml_verifier = XmlVerifier(repository)
	typer = Typer(repository)
	mover = PersonalizationRequestToCreatedMover(repository)
	destroyer = DestroyerFactory('undefined', 'end')(repository)

	with open('tests/example_file.xml', 'r', encoding='utf8') as f:
		text = f.read()
	
	assert file_saver(text)
	assert xml_verifier()
	assert typer()
	assert mover()
	assert destroyer()

	assert not xml_verifier()
	assert not typer()
	assert not mover()
	assert not destroyer()

	assert file_saver(text)
	assert xml_verifier()
	assert typer()
	assert mover()
	assert destroyer()

	shutil.rmtree('./dir_tree')