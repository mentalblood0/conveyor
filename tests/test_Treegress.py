import shutil
import dataclasses

from conveyor import Item
from conveyor.common import Model
from conveyor.workers import Transformer

from .common import *



type = 'undefined'
status = 'created'


def clear():
	repository._drop(type)
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)


def test_create():

	item = Item(
		type=type,
		status='created',
		chain_id='ideeee',
		data='lalala',
		data_digest='lololo',
		metadata={
			'message_id': 'lololo'
		}
	)

	assert repository.create(item)

	clear()


def test_get():

	item = Item(
		type=type,
		status=status,
		chain_id='ideeee',
		data='lalala',
		data_digest='lololo',
		metadata={
			'message_id': 'lololo'
		}
	)

	assert repository.create(item)
	assert repository.get(type, {'status': status}, limit=None)[0].metadata['message_id'] == item.metadata['message_id']

	clear()


def test_delete():

	assert repository.create(Item(
		type=type,
		status=status,
		chain_id='ideeee',
		data='lalala',
		data_digest='lololo',
		metadata={
			'message_id': 'lololo'
		}
	))
	id = repository.get(type, {'status': status})[0].id
	assert repository.delete(type, id)
	assert repository.get(type, {'status': status}) == []

	clear()


def test_cant_get_file_path():

	repository.create(Item(
		type=type,
		status=status
	))

	class W(Transformer):

		input_type = type
		input_status = status

		possible_output_statuses = ['got file path']

		def transform(self, item):
			print(item.metadata['file_path'])
			return self.possible_output_statuses[0]

	assert not W(repository)()

	clear()


def test_cant_set_file_path():

	repository.create(Item(
		type=type,
		status=status
	))

	class W(Transformer):

		input_type = type
		input_status = status

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

	model = Model(repository.db, type)
	assert not model.select().where(model.file_path=='lalala').execute()

	clear()


def test_reserve():

	for i in range(2):
		repository.create(Item(
			type=type,
			status=status
		))

	first_worker = 'lalala'
	second_worker = 'lololo'

	assert repository.reserve(
		type=type,
		status=status,
		id=first_worker,
		limit=1
	) == 1
	assert len(repository.get(
		type=type,
		where={'status': status},
		reserved_by=first_worker
	)) == 1

	assert repository.reserve(
		type=type,
		status=status,
		id=second_worker,
		limit=2
	) == 1
	assert len(repository.get(
		type=type,
		where={'status': status},
		reserved_by=second_worker
	)) == 1

	clear()


def test_reserve_intersection():

	repository.create(Item(
		type=type,
		status=status
	))
	
	model = Model(repository.db, type)

	first_query = (
		model
		.update(reserved_by='lalala')
		.where(
			model.id.in_(
				model
				.select(model.id)
				.where(
					model.reserved_by=='',
					model.status==status
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
					model.reserved_by=='',
					model.status==status
				)
				.limit(1)
			)
		)
	)

	assert first_query.execute() == 1
	assert second_query.execute() == 0

	clear()