import pytest
import typing
import datetime
import pydantic
import dataclasses

from conveyor.core import ItemQuery, ItemMask
from conveyor.repositories.Rows._Rows import _Rows, Row

from .common import *



@pytest.fixture
@pydantic.validate_arguments
def rows(db) -> _Rows:
	return _Rows(db)


@pytest.fixture
def row() -> Row:

	data = Row.Data(value=b'')

	return Row(
		type=Row.Type('type'),
		status=Row.Status('status'),
		digest=data.digest,
		metadata=Row.Metadata({
			Row.Metadata.Key('key'): 'value'
		}),
		chain=Row.Chain(ref=data).value,
		created=Row.Created(datetime.datetime.utcnow()),
		reserver=Row.Reserver(exists=False)
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
		lambda r: {'status':  Row.Status(r.status.value + '_')},
		lambda r: {'chain':   Row.Chain(ref=Row.Data(value=b'_')).value},
		lambda r: {'digest':  Row.Data.Digest(r.digest.value + b'_')},
		lambda r: {'created': Row.Created(r.created.value - datetime.timedelta(seconds=1))},
		lambda r: {'metadata':  Row.Metadata(r.metadata.value | {Row.Metadata.Key('key'): r.metadata.value[Row.Metadata.Key('key')] + '_'})}
	]
)
@pydantic.validate_arguments
def test_get_exact(rows: _Rows, row: Row, query_all: ItemQuery, changes: typing.Callable[[Row], dict[str, Row.Value]]):

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