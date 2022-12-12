import peewee
import pytest
import datetime
import pydantic
import dataclasses

from conveyor.core import ItemQuery, ItemMask
from conveyor.core.Item import Data, Reserver, Chain
from conveyor.repositories.Rows._Rows import _Rows, Row



db = peewee.SqliteDatabase(':memory:')


@pytest.fixture
def rows() -> _Rows:
	return _Rows(db)


@pytest.fixture
def row() -> Row:

	data = Data(value=b'')

	return Row(
		type=Row.Type('type'),
		status=Row.Status('status'),
		digest=data.digest,
		metadata=Row.Metadata({
			Row.Metadata.Key('key'): 'value'
		}),
		chain=Chain(ref=data).value,
		created=Row.Created(datetime.datetime.utcnow()),
		reserver=Reserver(exists=False)
	)


@pydantic.validate_arguments
def test_immutable(rows: _Rows):
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.db = b'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del rows.db
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.x = b'x'


@pydantic.validate_arguments
def test_append_get_delete(rows: _Rows, row: Row):

	rows.add(row)

	query = ItemQuery(
		mask=ItemMask(
			type=row.type
		),
		limit=None
	)
	saved_items = [*rows[query]]
	assert len(saved_items) == 1
	saved = saved_items[0]
	assert saved.type == row.type
	assert saved.status == row.status
	assert saved.digest == row.digest
	assert saved.metadata == row.metadata
	assert saved.chain == row.chain
	assert saved.created == row.created
	assert saved.reserver == row.reserver

	del rows[row]
	assert not len([*rows[query]])


@pydantic.validate_arguments
def test_delete_nonexistent(rows: _Rows, row: Row):
	del rows[row]