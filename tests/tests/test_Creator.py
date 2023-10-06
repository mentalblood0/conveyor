import pytest
import typing

from conveyor.core import Worker
from conveyor.core.Worker import processors
from conveyor.core import Query, Repository

from ..common import *



@pytest.fixture
def creator() -> processors.Creator:

	class C(processors.Creator):
		def process(self, config: typing.Iterable[Item]) -> typing.Iterable[Item]:
			return config

	return C()


@pytest.fixture
def worker(creator: processors.Creator, repository: Repository) -> Worker.Worker:
	return Worker.Worker(
		processor  = creator,
		repository = repository
	)


def test_creator_create_one_item(worker: Worker.Worker, item: Item, query_all: Query):
	for j in range(2):
		worker((item,))
		assert len(worker.repository) == j + 1
		for i in (*worker.repository[query_all],):
			assert i == item


def test_creator_create_many_items(worker: Worker.Worker, item: Item, query_all: Query):
	n = 3
	for j in range(2):
		worker((item,) * n)
		assert len(worker.repository) == n * (j + 1)
		for i in worker.repository[query_all]:
			assert i == item