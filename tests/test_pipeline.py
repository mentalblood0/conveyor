import os
import shutil
from logging.handlers import RotatingFileHandler

from tests.example_workers import *
from conveyor import LogsRepository
from conveyor.workers.factories import DestroyerFactory
from conveyor.processor_effects import ExceptionLogging
from conveyor.repository_effects import SimpleLogging, DbLogging

from .common import *



odd = '3'
another = str(-int(odd))
log_path = 'log.txt'


def clear():

	repository._drop('undefined')
	repository._drop('odd')
	repository._drop('even')
	repository._drop('another')
	repository._drop('product')

	shutil.rmtree(dir_tree_root_path, ignore_errors=True)

	try:
		os.remove(log_path)
	except Exception:
		pass


def crash(*args, **kwargs):
	raise Exception


def test_correct():

	DbLogging(repository, LogsRepository(db)).install(repository)
	SimpleLogging().install(repository)

	saver = Saver(repository)
	square_saver = AnotherSaver(repository)
	verifier = Verifier(repository)
	typer = Typer(repository)
	destroyer = DestroyerFactory('undefined', 'typed')(repository)
	multiplier = Multiplier(repository)

	assert saver(odd)
	assert len(verifier()) == 1
	assert len(typer()) == 1
	assert square_saver(another)
	source = repository.get('odd', {'status': 'created'})
	assert source
	linked = repository.get('another', {'status': 'created'})
	assert linked
	assert linked[0].chain_id == source[0].chain_id
	assert len(destroyer()) == 1
	assert len(multiplier()) == 1
	products = repository.get('product', {'status': 'created'}, limit=None)
	assert len(products) == 1

	assert not verifier()
	assert not typer()
	assert not destroyer()
	assert not multiplier()

	assert saver(odd)
	assert saver(odd)
	assert len(verifier()) == 2
	assert len(typer()) == 2
	assert square_saver(another)
	assert square_saver(another)
	assert len(destroyer()) == 2
	assert len(multiplier()) == 2
	products = repository.get('product', {'status': 'created'}, limit=None)
	assert len(products) == 1 + 2

	clear()


def test_exception_logging():

	saver = Saver(repository)
	verifier = Verifier(repository)

	verifier.transform = crash
	logging_effect = ExceptionLogging(
		handler=RotatingFileHandler(log_path),
		color=False
	)
	logging_effect.install(verifier)

	assert saver(odd)
	verifier()

	assert os.path.exists(log_path)
	with open(log_path) as f:
		log = f.read()
	
	assert len(log)
	assert 'Verifier' in log

	logging_effect.logger.removeHandler(logging_effect.handler)
	logging_effect.handler.close()
	clear()


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

	repository.update = crash
	print('-- typer')
	assert len(typer()) == 0
	assert len(repository.get(typer.possible_output_types[0], {'status': typer.output_status})) == 0

	clear()