import pytest
import typing
import dataclasses

from conveyor.core import Worker
from conveyor.core.Worker import processors
from conveyor.core import Mask, Query, Repository

from ..common import *



@pytest.fixture
def mover() -> processors.Mover:

	class M(processors.Mover):

		def process(self, input: Item) -> typing.Iterable[Item.Status | Item]:

			yield Item.Status(f'{input.status.value}_')

			n = input.metadata['n']
			match n:
				case int():
					for _ in range(n):
						yield dataclasses.replace(input, type = Item.Type('new'))
				case _:
					pass

	return M()


@pytest.fixture
def worker(receiver: Worker.Receiver, mover: processors.Mover, repository: Repository) -> Worker.Worker:
	return Worker.Worker(
		receiver   = receiver,
		processor  = mover,
		repository = repository
	)


def test_mover_change_status_create_one_item(worker: Worker.Worker, item: Item, query_all: Query):

	item = dataclasses.replace(item, metadata = item.metadata | {Item.Metadata.Key('n'): 1})
	status = item.status
	worker.repository.append(item)

	for _ in range(2):
		worker()
		assert len(worker.repository) == 2
		for i in worker.repository[query_all]:
			assert i == dataclasses.replace(item, status = Item.Status(f'{status.value}_'))
		for i in worker.repository[
			Query(
				mask = Mask(type = Item.Type('new')),
				limit = None
			)
		]:
			assert i == dataclasses.replace(item, type = Item.Type('new'))


def test_mover_change_status_create_many_items(worker: Worker.Worker, item: Item, query_all: Query):

	n = 3
	item = dataclasses.replace(item, metadata = item.metadata | {Item.Metadata.Key('n'): n})
	status = item.status
	worker.repository.append(item)

	for _ in range(2):
		worker()
		assert len(worker.repository) == 1 + n
		for i in worker.repository[query_all]:
			assert i == dataclasses.replace(item, status = Item.Status(f'{status.value}_'))
		for i in worker.repository[
			Query(
				mask = Mask(type = Item.Type('new')),
				limit = None
			)
		]:
			assert i == dataclasses.replace(item, type = Item.Type('new'))