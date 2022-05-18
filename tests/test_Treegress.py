import shutil
import pytest
import dataclasses
from peewee import CharField

from conveyor import Item
from conveyor.common import Model
from conveyor.workers import Transformer

from .common import *



type = 'undefined'
status = 'created'


@pytest.fixture
def pytest_item():
	return Item(
		type=type,
		status=status,
		data='lalala',
		metadata={
			'message_id': 'lololo'
		}
	)


@pytest.fixture(autouse=True)
def clear():
	repository._drop(type)
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)


def test_create(pytest_item):
	assert repository.create(pytest_item)


def test_update(pytest_item):

	repository.create(pytest_item)

	updated_item = dataclasses.replace(
		repository.get(pytest_item.type)[0],
		status='changed'
	)
	repository.update(updated_item)

	assert repository.get(pytest_item.type)[0] == updated_item


def test_get(pytest_item):
	assert repository.create(pytest_item)
	assert repository.get(pytest_item.type)[0].metadata['message_id'] == pytest_item.metadata['message_id']


def test_delete(pytest_item):

	assert repository.create(pytest_item)

	id = repository.get(pytest_item.type)[0].id
	assert repository.delete(pytest_item.type, id)
	assert repository.get(pytest_item.type) == []


def test_transaction(pytest_item):

	def create():
		for i in range(3):
			assert repository.create(pytest_item)
		raise KeyError

	transaction_create = repository.transaction(create)
	with pytest.raises(KeyError):
		transaction_create()

	assert not len(repository.get(pytest_item.type))


def test_cant_get_file_path(pytest_item):

	repository.create(pytest_item)

	class W(Transformer):

		input_type = pytest_item.type
		input_status = pytest_item.status

		possible_output_statuses = ['got file path']

		def transform(self, item):
			item.metadata['file_path']
			return self.possible_output_statuses[0]

	assert not W(repository)()


def test_cant_set_file_path(pytest_item):

	repository.create(pytest_item)

	class W(Transformer):

		input_type = pytest_item.type
		input_status = pytest_item.status

		possible_output_statuses = ['got file path']

		def transform(self, item):
			return dataclasses.replace(
				item,
				status=self.possible_output_statuses[0],
				metadata=item.metadata | {
					'file_path': 'lalala'
				}
			)

	assert W(repository)()
	assert not len(repository.get(pytest_item.type, {'file_path': 'lalala'}))


def test_reserve(pytest_item):

	for i in range(2):
		repository.create(pytest_item)

	first_worker = 'lalala'
	second_worker = 'lololo'

	assert repository.reserve(
		type=pytest_item.type,
		status=pytest_item.status,
		id=first_worker,
		limit=1
	) == 1
	assert len(repository.get(
		type=pytest_item.type,
		reserved_by=first_worker
	)) == 1

	assert repository.reserve(
		type=pytest_item.type,
		status=pytest_item.status,
		id=second_worker,
		limit=2
	) == 1
	assert len(repository.get(
		type=pytest_item.type,
		reserved_by=second_worker
	)) == 1


def test_reserve_intersection(pytest_item):

	repository.create(pytest_item)
	
	model = Model(repository.db, pytest_item.type)

	first_query = (
		model
		.update(reserved_by='lalala')
		.where(
			model.id.in_(
				model
				.select(model.id)
				.where(
					model.reserved_by==None,
					model.status==pytest_item.status
				)
				.limit(1)
			)
		)
	)
	second_query = (
		model
		.update(reserved_by='lololo')
		.where(
			model.id.in_(
				model
				.select(model.id)
				.where(
					model.reserved_by==None,
					model.status==pytest_item.status
				)
				.limit(1)
			)
		)
	)

	assert first_query.execute() == 1
	assert second_query.execute() == 0


def test_migration_add_column(pytest_item):
	repository.create(pytest_item)
	repository.create(dataclasses.replace(
		pytest_item,
		metadata=pytest_item.metadata | {
			'b': 2
		}
	))


def test_migration_drop_column(pytest_item):
	repository.create(pytest_item)
	repository.create(dataclasses.replace(pytest_item, metadata={}))


def test_migration_to_reserve_field():
	Model(
		repository.db,
		type,
		{
			'chain_id': CharField(max_length=63, index=True),
			'status': CharField(max_length=63, index=True),
			'data_digest': CharField(max_length=63)
		}
	)
	repository.reserve(type, status, 'test')