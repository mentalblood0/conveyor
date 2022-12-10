import peewee
import pytest
import pathlib
import datetime
import dataclasses

from conveyor.core import Item, Chain, ItemQuery, ItemMask
from conveyor.repositories.Joint import Joint, ItemsFiles, ItemsRows, Files, Rows



db = peewee.SqliteDatabase(':memory:')


@pytest.fixture
def item():

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
def joint():
	return Joint([
		ItemsRows(Rows(db)),
		ItemsFiles(Files(root=pathlib.Path('.'), suffix='.txt'))
	])


def test_immutable(joint: Joint):
	with pytest.raises(dataclasses.FrozenInstanceError):
		joint.parts = b'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del joint.parts
	with pytest.raises(dataclasses.FrozenInstanceError):
		joint.x = b'x'


def test_append_get_delete(joint: Joint, item: Item):

	joint.add(item)

	query = ItemQuery(
		mask=ItemMask(
			type=item.type
		),
		limit=None
	)
	saved_items = [*joint[query]]
	assert len(saved_items) == 1
	saved = saved_items[0]
	assert saved.type == item.type
	assert saved.status == item.status
	assert saved.data == item.data
	assert saved.metadata == item.metadata
	assert saved.chain == item.chain
	assert saved.created == item.created
	assert saved.reserved == item.reserved

	del joint[item]
	assert not len([*joint[query]])


def test_delete_nonexistent(joint, item):
	del joint[item]