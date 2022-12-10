import peewee
import pytest
import pathlib
import datetime
import pydantic
import dataclasses

from conveyor.repositories.Rows import _Rows, Rows
from conveyor.repositories.Files import _Files, Files
from conveyor.core import Item, Chain, ItemQuery, ItemMask, Repository



db = peewee.SqliteDatabase(':memory:')


@pytest.fixture
def item() -> Item:

	data = Item.Data(value=b'')

	return Item(
		type=Item.Type('type'),
		status=Item.Status('status'),
		data=data,
		metadata=Item.Metadata({
			Item.Metadata.Key('key'): 'value'
		}),
		chain=Chain(ref=data),
		created=Item.Created(datetime.datetime.utcnow()),
		reserved=False,
		reserver=None
	)

@pytest.fixture
def repository() -> Repository:
	return Repository([
		Rows(_Rows(db)),
		Files(_Files(root=pathlib.Path('.'), suffix='.txt'))
	])


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
		limit=None
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
	assert saved.reserved == item.reserved

	del repository[item]
	assert not len([*repository[query]])


@pydantic.validate_arguments
def test_delete_nonexistent(repository: Repository, item: Item):
	del repository[item]