import pytest
import typing
import datetime
import pydantic
import dataclasses

from conveyor.core import ItemQuery, ItemMask, Item
from conveyor.repositories.Rows._Rows import _Rows, Row

from .common import *



@pytest.fixture
@pydantic.validate_arguments
def rows(db) -> _Rows:
	return _Rows(db)


@pytest.fixture
def row() -> Row:

	data = Item.Data(value=b'')

	return Row(
		type=Item.Type('type'),
		status=Item.Status('status'),
		digest=data.digest,
		metadata=Item.Metadata({
			Item.Metadata.Key('key'): 'value'
		}),
		chain=Item.Chain(ref=data).value,
		created=Item.Created(datetime.datetime.utcnow()),
		reserver=Item.Reserver(exists=False)
	)


@pytest.fixture
def query_all(row) -> ItemQuery:
	return ItemQuery(
		mask=ItemMask(
			type=row.type
		),
		limit=128
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
		limit=128
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
	with pytest.raises(rows.OperationalError):
		del rows[row]


@pytest.mark.parametrize(
	'changes',
	[
		lambda r: {'status':   Item.Status(r.status.value + '_')},
		lambda r: {'chain':    Item.Chain(ref=Item.Data(value=b'_')).value},
		lambda r: {'digest':   Item.Data.Digest(r.digest.value + b'_')},
		lambda r: {'created':  Item.Created(r.created.value - datetime.timedelta(seconds=1))},
		lambda r: {'metadata': Item.Metadata(r.metadata.value | {Item.Metadata.Key('key'): r.metadata.value[Item.Metadata.Key('key')] + '_'})}
	]
)
@pydantic.validate_arguments
def test_get_exact(rows: _Rows, row: Row, query_all: ItemQuery, changes: typing.Callable[[Item], dict[str, Item.Value]]):

	rows.add(row)
	rows.add(dataclasses.replace(row, **changes(row)))
	assert len([*rows[query_all]]) == 2

	assert [*rows[
		ItemQuery(
			mask=ItemMask(
				type=row.type,
				status=row.status
			),
			limit=1
		)
	]][0] == row

	for r in rows[query_all]:
		del rows[r]