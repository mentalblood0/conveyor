import pytest
from peewee import fn

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


@pytest.fixture
def exceptions():
	return [IndexError('lalala'), AttributeError('lololo')]


def crash(exception):
	raise exception


def count(table):
	return table.select(fn.COUNT())


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
	assert count(errors_table) == 1


def test_Processor(item, exception, logger, errors_table):

	repository.create(item)

	worker = composeProcessor(exception)
	logger.install(worker)

	worker()
	assert count(errors_table) == 1


def test_repeat(item, exception, logger, errors_table):

	repository.create(item)
	result_item = repository.get(type)[0]

	worker = composeProcessor(exception)
	logger.install(worker)

	date_first = None
	date_last = None
	for i in range(3):

		worker()
		assert count(errors_table) == 1

		result = errors_table.select()[0]

		assert result.date_first
		assert result.date_last
		assert result.count == i + 1
		assert result.worker_name == worker.__class__.__name__
		assert result.item_type == item.type
		assert result.item_status == item.status
		assert result.item_chain_id == ''
		assert str(result.item_id) == result_item.id
		assert result.error_type == exception.__class__.__name__
		assert result.error_text == str(exception)

		if date_first is None:
			date_first = result.date_first
		else:
			assert date_first == result.date_first

		assert result.date_last != date_last
		date_last = result.date_last


def test_delete(item, exception, logger, errors_table):

	repository.create(item)

	worker = composeProcessor(exception)
	logger.install(worker)

	worker()

	worker.processItem = lambda item: item
	worker()

	assert count(errors_table) == 0


def test_delete_all(item, exceptions, logger, errors_table):

	repository.create(item)

	workers = [
		composeProcessor(e)
		for e in exceptions
	]
	for w in workers:
		logger.install(w)

	for w in workers:
		w()

	assert count(errors_table) == len(workers)

	workers[0].processItem = lambda item: item
	workers[0]()

	assert count(errors_table) == 0