import pytest
import datetime
import sqlalchemy

from conveyor.core import Item



@pytest.fixture
def db() -> sqlalchemy.engine.Engine:
	return sqlalchemy.create_engine("sqlite://", echo=True)


@pytest.fixture
def item() -> Item:

	data = Item.Data(value=b'')

	return Item(
		type=Item.Type('type'),
		status=Item.Status('status'),
		data=data,
		metadata=Item.Metadata({Item.Metadata.Key('key'): 'value'}),
		chain=Item.Chain(ref=data),
		created=Item.Created(value=datetime.datetime.utcnow()),
		reserver=Item.Reserver(exists=False)
	)