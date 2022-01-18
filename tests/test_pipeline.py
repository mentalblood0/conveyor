import os
import shutil
import pytest
from peewee import PostgresqlDatabase, OperationalError

from tests import config
from tests.example_workers import *
from conveyor.workers.factories import DestroyerFactory
from conveyor.item_repositories import DefaultItemRepository, FileRepository, MetadataRepository




dir_tree_root_path = 'dir_tree'


def test_incorrect():

	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	db = PostgresqlDatabase(
		config.db['db'], 
		user=config.db['user'], 
		password='', 
		host=config.db['host'], 
		port=config.db['port']
	)
	repository = DefaultItemRepository(
		dir_tree_root_path=dir_tree_root_path,
		file_repository=FileRepository(),
		metadata_repository=MetadataRepository(db=db)
	)	

	with open('tests/example_file.xml', 'r', encoding='utf8') as f:
		text = f.read()
	
	with pytest.raises(OperationalError):
		FileSaver(repository)(text)
	
	assert not os.listdir(os.path.join(dir_tree_root_path, 'undefined', '0'))

	shutil.rmtree(dir_tree_root_path)


def test_correct():

	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	db = PostgresqlDatabase(
		config.db['db'], 
		user=config.db['user'], 
		password=config.db['password'], 
		host=config.db['host'], 
		port=config.db['port']
	)
	repository = DefaultItemRepository(
		dir_tree_root_path=dir_tree_root_path,
		file_repository=FileRepository(),
		metadata_repository=MetadataRepository(db=db)
	)

	repository.transaction().drop('conveyor_log').execute()
	repository.transaction().drop('undefined').execute()
	repository.transaction().drop('PersonalizationRequest').execute()

	file_saver = FileSaver(repository)
	xml_verifier = XmlVerifier(repository)
	typer = Typer(repository)
	mover = PersonalizationRequestToCreatedMover(repository)
	destroyer = DestroyerFactory('undefined', 'end')(repository)

	with open('tests/example_file.xml', 'r', encoding='utf8') as f:
		text = f.read()
	
	assert file_saver(text)
	assert len(xml_verifier()) == 1
	assert len(typer()) == 1
	assert len(mover()) == 1
	assert len(destroyer()) == 1

	assert not xml_verifier()
	assert not typer()
	assert not mover()
	assert not destroyer()

	assert file_saver(text)
	assert file_saver(text)
	assert len(xml_verifier()) == 2
	assert len(typer()) == 2
	assert len(mover()) == 2
	assert len(destroyer()) == 2

	shutil.rmtree(dir_tree_root_path)