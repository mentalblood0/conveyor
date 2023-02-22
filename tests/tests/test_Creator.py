import pytest
import typing
import pydantic

from conveyor.core import Worker
from conveyor.core.Worker import processors
from conveyor.core import Query, Repository

from ..common import *



@pytest.fixture
def creator() -> processors.Creator:

	class C(processors.Creator):
		def process(self, config: dict[str, typing.Any]) -> typing.Iterable[Item]:
			for i in config['items']:
				match i:
					case Item():
						yield i
					case _:
						pass

	return C()


@pytest.fixture
@pydantic.validate_arguments
def worker(creator: processors.Creator, repository: Repository) -> Worker.Worker:
	return Worker.Worker(
		processor  = creator,
		repository = repository
	)


@pydantic.validate_arguments
def test_creator_create_one_item(worker: Worker.Worker, item: Item, query_all: Query):
	for j in range(2):
		worker({'items': (item,)})
		assert len(worker.repository) == j + 1
		for i in worker.repository[query_all]:
			assert i == item


@pydantic.validate_arguments
def test_creator_create_many_items(worker: Worker.Worker, item: Item, query_all: Query):
	n = 3
	for j in range(2):
		worker({'items': (item,) * n})
		assert len(worker.repository) == n * (j + 1)
		for i in worker.repository[query_all]:
			assert i == item