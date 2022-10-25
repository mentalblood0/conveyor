import time
import shutil
import pytest
import threading
import itertools
import dataclasses
from peewee import CharField

from conveyor import Item
from conveyor.common import Model
from conveyor.workers import Transformer, Mover

from .common import *



type = 't'
status = 's'


@pytest.fixture
def item():
	return Item(
		type=type,
		status=status,
		data='d',
		metadata={
			'a': 1
		}
	)


@pytest.fixture(autouse=True)
def clear():
	repository._drop(type)
	repository._drop('A')
	repository._drop('B')
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)
	Model.cache.clear()


def test_create(item):
	assert repository.create(item)


def test_update(item):

	repository.create(item)

	updated_item = dataclasses.replace(
		repository.get(item.type)[0],
		status='changed'
	)
	repository.update(updated_item)

	assert repository.get(item.type)[0] == updated_item


def test_get(item):
	assert repository.create(item)
	assert repository.get(item.type)[0].metadata['a'] == item.metadata['a']


def test_delete(item):

	assert repository.create(item)

	id = repository.get(item.type)[0].id
	assert repository.delete(item.type, id)
	assert repository.get(item.type) == []


def test_transaction(item):

	def create():
		for i in range(3):
			assert repository.create(item)
		raise KeyError

	transaction_create = repository.transaction(create)
	with pytest.raises(KeyError):
		transaction_create()

	Model.cache.clear()

	assert not len(repository.get(item.type))


def test_cant_set_file_path(item):

	repository.create(item)

	class W(Transformer):

		input_type = item.type
		input_status = item.status

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
	assert not len(repository.get(item.type, {'file_path': 'lalala'}))


def test_reserve(item):

	for i in range(2):
		repository.create(item)

	first_worker = 'lalala'
	second_worker = 'lololo'

	assert repository.reserve(
		type=item.type,
		status=item.status,
		id=first_worker,
		limit=1
	) == 1
	assert len(repository.get(
		type=item.type,
		reserved_by=first_worker
	)) == 1

	assert repository.reserve(
		type=item.type,
		status=item.status,
		id=second_worker,
		limit=2
	) == 1
	assert len(repository.get(
		type=item.type,
		reserved_by=second_worker
	)) == 1


def test_reserve_intersection(item):

	repository.create(item)
	
	model = Model(repository.db, item.type)

	first_query = (
		model
		.update(reserved_by='lalala')
		.where(
			model.id.in_(
				model
				.select(model.id)
				.where(
					model.reserved_by==None,
					model.status==item.status
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
					model.status==item.status
				)
				.limit(1)
			)
		)
	)

	assert first_query.execute() == 1
	assert second_query.execute() == 0


# def test_workers_parallel(item):

# 	a_number = 2
# 	b_number = 1
# 	runs_number = 10

# 	class A(Mover):

# 		input_type = 'A'
# 		input_status = status
# 		moved_status = 'end'

# 		possible_output_types = ['B']
# 		output_status = status

# 		def transform(self, item):
# 			return dataclasses.replace(item, type='B')

# 	class B(Mover):

# 		input_type = 'B'
# 		input_status = status
# 		moved_status = 'end'

# 		possible_output_types = ['A']
# 		output_status = status

# 		def transform(self, item):
# 			return dataclasses.replace(item, type='A')

# 	repository.create(dataclasses.replace(item, type='A'))

# 	a_workers = [A(repository) for i in range(a_number)]
# 	b_workers = [B(repository) for i in range(b_number)]

# 	def run_worker(w, n):
# 		for i in range(n):
# 			w()

# 	a_threads = [
# 		threading.Thread(target=run_worker, args=(w, runs_number))
# 		for w in a_workers
# 	]
# 	b_threads = [
# 		threading.Thread(target=run_worker, args=(w, runs_number))
# 		for w in b_workers
# 	]

# 	for t in b_threads:
# 		t.start()
# 	for t in a_threads:
# 		t.start()

# 	while any(t.is_alive() for t in itertools.chain(a_threads, b_threads)):
# 		time.sleep(0.05)

# 	assert (
# 		len(repository.get('A', where={'status': status}, limit=None)) + 
# 		len(repository.get('B', where={'status': status}, limit=None))
# 	) == 1


def test_migration_add_column(item):
	repository.create(item)
	repository.create(dataclasses.replace(
		item,
		metadata=item.metadata | {
			'b': 2
		}
	))


# def test_migration_drop_column(item):
# 	repository.create(item)
# 	repository.create(dataclasses.replace(item, metadata={}))
# 	assert not repository.get(item.type)[0].metadata