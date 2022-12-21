import typing
import pytest
import pathlib
import pydantic
import dataclasses

from conveyor.repositories.Rows import _Rows, Rows
from conveyor.repositories.Files import _Files, Files
from conveyor.core import Item, ItemQuery, ItemMask, Repository

from .common import *


@pytest.fixture
@pydantic.validate_arguments
def repository(db) -> Repository:
	return Repository([
		Rows(_Rows(db)),
		Files(_Files(root=pathlib.Path('.'), suffix='.txt'))
	])


@pytest.fixture
@pydantic.validate_arguments
def query_all(item: Item) -> ItemQuery:
	return ItemQuery(
		mask=ItemMask(
			type=item.type
		),
		limit=128
	)


@pydantic.validate_arguments
def test_immutable(repository: Repository):
	with pytest.raises(dataclasses.FrozenInstanceError):
		repository.parts = b'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del repository.parts
	with pytest.raises(dataclasses.FrozenInstanceError):
		repository.x = b'x'


@pydantic.validate_arguments
def test_append_get_delete(repository: Repository, item: Item):

	repository.add(item)

	query = ItemQuery(
		mask=ItemMask(
			type=item.type
		),
		limit=128
	)
	saved_items = [*repository[query]]
	assert len(saved_items) == 1
	saved = saved_items[0]
	assert saved.type == item.type
	assert saved.status == item.status
	assert saved.data == item.data
	assert saved.metadata == item.metadata
	assert saved.chain == item.chain
	assert saved.created == item.created
	assert saved.reserver.exists

	del repository[saved]
	assert not len([*repository[query]])


@pydantic.validate_arguments
def test_delete_nonexistent(repository: Repository, item: Item):
	del repository[item]


@pytest.mark.parametrize(
	'changes',
	[
		lambda r: {'status':   Item.Status(r.status.value + '_')},
		lambda r: {'chain':    Item.Chain(ref=Item.Data(value=b'_'))},
		lambda r: {'data':     Item.Data(value=r.data.value + b'_')},
		lambda r: {'created':  Item.Created(r.created.value - datetime.timedelta(seconds=1))},
		lambda r: {'metadata': Item.Metadata(r.metadata.value | {Item.Metadata.Key('key'): r.metadata.value[Item.Metadata.Key('key')] + '_'})}
	]
)
@pydantic.validate_arguments
def test_get_exact(repository: Repository, item: Item, query_all: ItemQuery, changes: typing.Callable[[Item], dict[str, Item.Value]]):

	repository.add(item)

	for index, i in enumerate([*repository[query_all]]):
		repository[i] = i

	changed_item = dataclasses.replace(item, **changes(item))
	repository.add(changed_item)

	for index, i in enumerate([*repository[query_all]]):
		repository[i] = i

	both = [*repository[query_all]]
	assert len(both) == 2
	for i in both:
		repository[i] = i

	assert [*repository[
		ItemQuery(
			mask=ItemMask(
				type=item.type,
				status=item.status
			),
			limit=1
		)
	]][0] == item

	for r in repository[query_all]:
		del repository[r]