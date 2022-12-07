import peewee
import pytest
import datetime
import dataclasses

from conveyor.repositories.Filows import Rows, RowsItem
from conveyor.core import Item, Chain, ItemQuery, ItemMask



db = peewee.SqliteDatabase(':memory:')


@pytest.fixture
def rows():
	return Rows(db)


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
		reserved=None
	)


def test_immutable(rows: Rows):
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.db = b'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del rows.db
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.x = b'x'


def test_append_get_delete(rows: Rows, item: Item):

	rows.add(RowsItem(item))

	query = ItemQuery(
		mask=ItemMask(
			type=item.type
		),
		limit=None
	)
	saved_items = [*rows[query]]
	assert len(saved_items) == 1
	saved = saved_items[0]
	assert saved.type == item.type
	assert saved.status == item.status
	assert saved.digest == item.data.digest
	assert saved.metadata == item.metadata
	assert saved.chain == item.chain.value
	assert saved.created == item.created
	assert saved.reserved == item.reserved

	del rows[RowsItem(item)]
	assert not len([*rows[query]])


def test_delete_nonexistent(rows, item):
	del rows[RowsItem(item)]