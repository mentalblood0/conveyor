import shutil
from peewee import PostgresqlDatabase

from tests import config
from tests.example_workers import *
from conveyor import LogsRepository
from conveyor.repositories import Treegres
from conveyor.repository_effects import SimpleLogging, DbLogging
from conveyor.workers.factories import LinkerFactory, DestroyerFactory




dir_tree_root_path = 'dir_tree'


def test_correct():

	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	db = PostgresqlDatabase(
		config.db['db'],
		user=config.db['user'],
		password=config.db['password'],
		host=config.db['host'],
		port=config.db['port']
	)

	repository = Treegres(
		db=db,
		dir_tree_root_path=dir_tree_root_path
	)
	repository._drop('conveyor_log')
	repository._drop('undefined')
	repository._drop('PersonalizationRequest')
	repository._drop('PrintTask')

	DbLogging(repository, LogsRepository(db)).install(repository)
	SimpleLogging().install(repository)

	file_saver = FileSaver(repository)
	another_file_saver = PrintTaskSaver(repository)
	xml_verifier = XmlVerifier(repository)
	typer = Typer(repository)
	mover = PersonalizationRequestToCreatedMover(repository)
	linker = LinkerFactory(
		input_type='PrintTask',
		input_status='created',
		source_type='PersonalizationRequest',
		source_status='created',
		output_status='linked_to_PersonalizationRequest',
		metadata_field='message_id'
	)(repository)
	destroyer = DestroyerFactory('undefined', 'end')(repository)

	with open('tests/example_file.xml', 'r', encoding='utf8') as f:
		text = f.read()
	
	assert file_saver(text)
	assert len(xml_verifier()) == 1
	assert len(typer()) == 1
	assert len(mover()) == 1
	assert another_file_saver(text)
	assert len(linker()) == 1
	source = repository.fetch('PersonalizationRequest', 'created')
	linked = repository.fetch('PrintTask', 'linked_to_PersonalizationRequest')
	assert linked
	assert linked[0].chain_id == source[0].chain_id
	assert len(destroyer()) == 1

	assert not xml_verifier()
	assert not typer()
	assert not mover()
	assert not linker()
	assert not destroyer()

	assert file_saver(text)
	assert file_saver(text)
	assert len(xml_verifier()) == 2
	assert len(typer()) == 2
	assert len(mover()) == 2
	assert len(destroyer()) == 2

	shutil.rmtree(dir_tree_root_path, ignore_errors=True)


def test_mover_transaction():

	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	db = PostgresqlDatabase(
		config.db['db'],
		user=config.db['user'],
		password=config.db['password'],
		host=config.db['host'],
		port=config.db['port']
	)

	repository = Treegres(
		db=db,
		dir_tree_root_path=dir_tree_root_path
	)
	repository._drop('conveyor_log')
	repository._drop('undefined')
	repository._drop('PersonalizationRequest')

	DbLogging(repository, LogsRepository(db)).install(repository)
	SimpleLogging().install(repository)

	file_saver = FileSaver(repository)
	xml_verifier = XmlVerifier(repository)
	typer = Typer(repository)
	mover = PersonalizationRequestToCreatedMover(repository)

	with open('tests/example_file.xml', 'r', encoding='utf8') as f:
		text = f.read()
	
	print('-- file_saver')
	assert file_saver(text)
	print('-- xml_verifier')
	assert len(xml_verifier()) == 1
	print('-- typer')
	assert len(typer()) == 1

	def crash(*args, **kwargs):
		raise Exception
	repository.update = crash
	print('-- mover')
	assert len(mover()) == 0
	assert len(repository.fetch(mover.output_type, mover.output_status)) == 0

	shutil.rmtree(dir_tree_root_path, ignore_errors=True)