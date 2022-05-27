import pytest

from conveyor.common import Model
from conveyor.core import Item, Creator, Processor
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


def composeProcessor(exception):

	class P(Processor):

		input_type = type
		input_status = status

		def processItem(self, item):
			crash(exception)
			return item

	return P(repository)


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
	assert result.item_id == -1
	assert result.error_type == exception.__class__.__name__
	assert result.error_text == str(exception)


def test_Processor(item, exception, logger, errors_table):

	repository.create(item)
	result_item = repository.get(type)[0]

	worker = composeProcessor(exception)
	logger.install(worker)

	worker()
	assert len(errors_table.select()) == 1

	result = errors_table.select()[0]
	assert result.date
	assert result.worker_name == worker.__class__.__name__
	assert result.item_type == item.type
	assert result.item_status == item.status
	assert result.item_chain_id == result_item.chain_id
	assert str(result.item_id) == result_item.id
	assert result.error_type == exception.__class__.__name__
	assert result.error_text == str(exception)


def test_repeat(item, exception, logger, errors_table):

	repository.create(item)
	result_item = repository.get(type)[0]

	worker = composeProcessor(exception)
	logger.install(worker)

	old_date = None
	for _ in range(3):

		worker()
		assert len(errors_table.select()) == 1

		result = errors_table.select()[0]

		assert result.date
		assert result.worker_name == worker.__class__.__name__
		assert result.item_type == item.type
		assert result.item_status == item.status
		assert result.item_chain_id == ''
		assert str(result.item_id) == result_item.id
		assert result.error_type == exception.__class__.__name__
		assert result.error_text == str(exception)

		assert result.date != old_date
		old_date = result.date