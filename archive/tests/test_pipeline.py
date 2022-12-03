import os
import shutil
import pytest
from logging.handlers import RotatingFileHandler

from tests.example_workers import *
from conveyor.workers.factories import DestroyerFactory
from conveyor.processor_effects import ExceptionLogging

from .common import *



odd = '3'
another = str(-int(odd))


@pytest.fixture(autouse=True)
def clearDb():
	repository._drop('undefined')
	repository._drop('odd')
	repository._drop('even')
	repository._drop('another')
	repository._drop('product')


def crash(*args, **kwargs):
	raise Exception


def test_correct():

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


def test_mover_transaction():

	saver = Saver(repository)
	verifier = Verifier(repository)
	typer = Typer(repository)

	assert saver(odd)
	assert len(verifier()) == 1

	object.__setattr__(repository, 'update', crash)
	assert len(typer()) == 0
	assert len(repository.get(typer.possible_output_types[0], {'status': typer.output_status})) == 0