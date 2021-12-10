import shutil
from peewee import PostgresqlDatabase

from conveyor.workers.factories import DestroyerFactory
from conveyor.item_repositories import DefaultItemRepository
from tests import ToPersonalizationRequestMover, config, FileSaver, XmlVerifier, Typer



db = PostgresqlDatabase(
	config.db['db'], 
	user=config.db['user'], 
	password=config.db['password'], 
	host=config.db['host'], 
	port=config.db['port']
)
repository = DefaultItemRepository(db, 'dir_tree')


def test_example():

	shutil.rmtree('dir_tree', ignore_errors=True)

	file_saver = FileSaver(repository)
	xml_verifier = XmlVerifier(repository)
	typer = Typer(repository)
	mover = ToPersonalizationRequestMover(repository)
	destroyer = DestroyerFactory('undefined', 'end')

	with open('tests/example_file.xml', 'rb') as f:
		text = f.read()
	
	assert file_saver(text)
	assert xml_verifier()
	assert typer()
	assert mover()
	assert destroyer()

	# shutil.rmtree('./dir_tree')