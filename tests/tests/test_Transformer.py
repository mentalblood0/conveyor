import enum
import pytest
import typing
import pydantic
import dataclasses

from conveyor.core import Worker
from conveyor.core.Worker import processors
from conveyor.core import Query, Repository

from ..common import *



class TransformerChanges(enum.Enum):
	status          = 1
	metadata_add    = 2
	metadata_delete = 3


@pytest.fixture
def transformer(transformer_changes: typing.Sequence[TransformerChanges]) -> processors.Transformer:

	class T(processors.Transformer):
		def process(self, input: Item) -> typing.Iterable[Item.Status | Item.Metadata]:
			for c in transformer_changes:
				match c:
					case TransformerChanges.status:
						yield Item.Status(f'{input.status.value}_')
					case TransformerChanges.metadata_add:
						yield Item.Metadata({Item.Metadata.Key('new'): 1})
					case TransformerChanges.metadata_delete:
						yield Item.Metadata({})

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
@pytest.mark.parametrize(
	'transformer_changes', ((TransformerChanges.status,),)
)
def test_transformer_change_status(worker: Worker.Worker, item: Item, query_all: Query):

	status = item.status
	worker.repository.append(item)

	for _ in range(2):
		worker()
		assert len(worker.repository) == 1
		for i in worker.repository[query_all]:
			assert i == dataclasses.replace(item, status = Item.Status(f'{status.value}_'))


@pydantic.validate_arguments
@pytest.mark.parametrize(
	'transformer_changes', ((TransformerChanges.metadata_add,),)
)
def test_transformer_add_metadata(worker: Worker.Worker, item: Item, query_all: Query):

	metadata = item.metadata
	worker.repository.append(item)

	for _ in range(2):
		worker()
		assert len(worker.repository) == 1
		for i in worker.repository[query_all]:
			assert i == dataclasses.replace(
				item,
				metadata = Item.Metadata(metadata.value | {Item.Metadata.Key('new'): 1})
			)


@pydantic.validate_arguments
@pytest.mark.parametrize(
	'transformer_changes', ((TransformerChanges.metadata_delete,),)
)
def test_transformer_delete_metadata(worker: Worker.Worker, item: Item, query_all: Query):
	worker.repository.append(item)
	for _ in range(2):
		worker()
		assert len(worker.repository) == 1
		for i in worker.repository[query_all]:
			assert i == item