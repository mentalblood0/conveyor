import os
import pytest
from logging.handlers import RotatingFileHandler

from conveyor.core import Item, Creator
from conveyor.workers import Transformer
from conveyor.processor_effects import ExceptionLogging

from .common import *



type = 'undefined'
status = 'created'
log_path = 'log.txt'


@pytest.fixture(autouse=True)
def clearDb():
	repository._drop(type)
	try:
		os.remove(log_path)
	except Exception:
		pass


@pytest.fixture
def item():
	return Item(
		type=type,
		status=status,
		data='d'
	)


@pytest.fixture
def logger():
	return ExceptionLogging(
		handler=RotatingFileHandler(log_path),
		color=False
	)


@pytest.fixture
def exception():
	return IndexError('lalala')


def crash(exception):
	raise exception


def composeCreator(item, exception):

	class C(Creator):

		output_type = type
		output_status = status

		def create(self):
			crash(exception)
			return item

	return C(repository)


def composeTransformer(exception):

	class T(Transformer):

		input_type = type
		input_status = status

		possible_output_statuses = ['end']

		def transform(self, item):
			crash(exception)
			return self.possible_output_statuses[0]

	return T(repository)


def test_Creator(item, exception, logger):

	worker = composeCreator(item, exception)
	logger.install(worker)

	worker()

	assert os.path.exists(log_path)
	with open(log_path) as f:
		log = f.read()
	
	assert len(log)

	logger.logger.removeHandler(logger.handler)
	logger.handler.close()


def test_Transformer(item, exception, logger):

	repository.create(item)

	worker = composeTransformer(exception)
	logger.install(worker)

	worker()

	logger.logger.removeHandler(logger.handler)
	logger.handler.close()