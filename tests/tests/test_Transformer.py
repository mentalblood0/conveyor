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
def transformer() -> processors.Transformer:

	class T(processors.Transformer):
		def process(self, input: Item) -> typing.Iterable[Item.Status | Item.Metadata]:
			yield Item.Status(f'{input.status}_')

	return T()


@pytest.fixture
@pydantic.validate_arguments
def worker(receiver: Worker.Receiver, transformer: processors.Transformer, repository: Repository) -> Worker.Worker:
	return Worker.Worker(
		receiver   = receiver,
		processor  = transformer,
		repository = repository
	)


@pydantic.validate_arguments
def test_transformer_change_status(worker: Worker.Worker, item: Item, query_all: Query):
	status = item.status
	worker.repository.append(item)
	worker()
	assert [*worker.repository[query_all]][0] == dataclasses.replace(item, status = Item.Status(f'{status}_'))