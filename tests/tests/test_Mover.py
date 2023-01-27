import pytest
import typing
import pydantic
import dataclasses

from conveyor.core import Worker
from conveyor.core.Worker import processors
from conveyor.core import Mask, Query, Repository

from ..common import *



@pytest.fixture
@pydantic.validate_arguments
def receiver(item: Item) -> Worker.Receiver:
	return Worker.Receiver((
		lambda _: Mask(
			type = item.type
		),
	))


@pytest.fixture
def mover() -> processors.Mover:

	class M(processors.Mover):
		def process(self, input: Item) -> typing.Iterable[Item.Status | Item]:
			yield Item.Status(f'{input.status}_')
			yield dataclasses.replace(input, type = Item.Type('new'))

	return M()


@pytest.fixture
@pydantic.validate_arguments
def worker(receiver: Worker.Receiver, mover: processors.Mover, repository: Repository) -> Worker.Worker:
	return Worker.Worker(
		receiver   = receiver,
		processor  = mover,
		repository = repository
	)


@pydantic.validate_arguments
def test_mover_change_status_create_one_item(worker: Worker.Worker, item: Item, query_all: Query):
	status = item.status
	worker.repository.append(item)
	worker()
	assert [*worker.repository[query_all]][0] == dataclasses.replace(item, status = Item.Status(f'{status}_'))
	assert [*worker.repository[
		Query(
			mask = Mask(type = Item.Type('new')),
			limit = None
		)
	]][0] == dataclasses.replace(item, type = Item.Type('new'))