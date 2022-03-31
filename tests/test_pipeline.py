import shutil

from tests.example_workers import *
from conveyor import LogsRepository
from conveyor.workers.factories import DestroyerFactory
from conveyor.repository_effects import SimpleLogging, DbLogging

from .common import *



odd = '3'
another = str(-int(odd))


def test_correct():

	DbLogging(repository, LogsRepository(db)).install(repository)
	SimpleLogging().install(repository)

	saver = Saver(repository)
	square_saver = AnotherSaver(repository)
	verifier = Verifier(repository)
	typer = Typer(repository)
	destroyer = DestroyerFactory('undefined', 'typed')(repository)

	assert saver(odd)
	assert len(verifier()) == 1
	assert len(typer()) == 1
	assert square_saver(another)
	source = repository.fetch('odd', 'created')
	assert source
	linked = repository.fetch('another', 'created')
	assert linked
	assert linked[0].chain_id == source[0].chain_id
	assert len(destroyer()) == 1

	assert not verifier()
	assert not typer()
	assert not destroyer()

	assert saver(odd)
	assert saver(odd)
	assert len(verifier()) == 2
	assert len(typer()) == 2
	assert len(destroyer()) == 2

	repository._drop('undefined')
	repository._drop('odd')
	repository._drop('another')
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)


def test_mover_transaction():

	DbLogging(repository, LogsRepository(db)).install(repository)
	SimpleLogging().install(repository)

	saver = Saver(repository)
	verifier = Verifier(repository)
	typer = Typer(repository)
	
	print('-- saver')
	assert saver(odd)
	print('-- verifier')
	assert len(verifier()) == 1

	def crash(*args, **kwargs):
		raise Exception
	repository.update = crash
	print('-- typer')
	assert len(typer()) == 0
	assert len(repository.fetch(typer.possible_output_types[0], typer.output_status)) == 0

	repository._drop('undefined')
	repository._drop('odd')
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)