import peewee
import pytest
import datetime

from conveyor.core import Item



@pytest.fixture
def db() -> peewee.Database:
	return peewee.SqliteDatabase(':memory:')


@pytest.fixture
def item() -> Item:

	data = Item.Data(value=b'')

	return Item(
		type=Item.Type('type'),
		status=Item.Status('status'),
		data=data,
		metadata=Item.Metadata({Item.Metadata.Key('a'): 'a'}),
		chain=Item.Chain(ref=data),
		created=Item.Created(value=datetime.datetime.utcnow()),
		reserver=Item.Reserver(exists=False)
	)