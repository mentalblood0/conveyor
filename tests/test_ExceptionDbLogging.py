import pytest

from conveyor.common import Model
from conveyor.core import Item, Creator
from conveyor.workers import Transformer
from conveyor.processor_effects import ExceptionDbLogging
from conveyor.processor_effects.ExceptionDbLogging import ExceptionLogsRepository

from .common import *



type = 'undefined'
status = 'created'
errors_table_name = 'errors'


@pytest.fixture(autouse=True)
def clearDb():
	repository._drop(type)
	repository._drop(errors_table_name)


@pytest.fixture
def item():
	return Item(
		type=type,
		status=status,
		data='d'
	)


@pytest.fixture
def logger():
	return ExceptionDbLogging(ExceptionLogsRepository(repository.db, errors_table_name))


@pytest.fixture
def errors_table():
	return Model(repository.db, errors_table_name)


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


def test_Creator(item, exception, logger, errors_table):

	worker = composeCreator(item, exception)
	logger.install(worker)

	worker()
	assert len(errors_table.select()) == 1

	result = errors_table.select()[0]
	assert result.date
	assert result.worker_name == worker.__class__.__name__
	assert result.item_type == item.type
	assert result.item_status == item.status
	assert result.item_chain_id == ''
	assert result.error_type == exception.__class__.__name__
	assert result.error_text == str(exception)


def test_Transformer(item, exception, logger, errors_table):

	repository.create(item)
	result_item = repository.get(type)[0]

	worker = composeTransformer(exception)
	logger.install(worker)

	worker()
	assert len(errors_table.select()) == 1

	result = errors_table.select()[0]
	assert result.date
	assert result.worker_name == worker.__class__.__name__
	assert result.item_type == item.type
	assert result.item_status == item.status
	assert result.item_chain_id == result_item.chain_id
	assert result.error_type == exception.__class__.__name__
	assert result.error_text == str(exception)