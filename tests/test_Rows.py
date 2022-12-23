import pytest
import typing
import datetime
import pydantic
import itertools
import dataclasses

from conveyor.core import ItemQuery, ItemMask, Item
from conveyor.repositories.Rows.Rows_ import Rows_, Row

from .common import *



@pytest.fixture
@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def rows(db: peewee.Database) -> Rows_:
	return Rows_(db)


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
def query_all(row: Row) -> ItemQuery:
	return ItemQuery(
		mask=ItemMask(
			type=row.type
		),
		limit=128
	)


@pydantic.validate_arguments
def test_immutable(rows: Rows_):
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.__setattr__('db', b'x')
	with pytest.raises(dataclasses.FrozenInstanceError):
		del rows.db
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.__setattr__('x', b'x')


@pydantic.validate_arguments
def test_append_get_delete(rows: Rows_, row: Row):

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
def test_delete_nonexistent(rows: Rows_, row: Row):
	with pytest.raises(rows.OperationalError):
		del rows[row]


@pytest.fixture
def changed_row(row: Row, changes_list: typing.Iterable[str]) -> Row:

	changes: dict[str, Item.Value | Item.Metadata] = {}

	for key in changes_list:
		value: Item.Value | Item.Metadata | None = None
		match key:
			case 'status':
				value = Item.Status(row.status.value + '_')
			case 'chain':
				value = row.chain + '_'
			case 'created':
				value = Item.Created(row.created.value - datetime.timedelta(seconds=1))
			case 'metadata':
				current = row.metadata.value[Item.Metadata.Key('key')]
				match current:
					case str():
						new = '_'
					case _:
						raise ValueError
				value = Item.Metadata(row.metadata.value | {Item.Metadata.Key('key'): new})
			case _:
				continue
		changes[key] = value

	return dataclasses.replace(row, **changes)


@pytest.mark.parametrize(
	'changes_list',
	itertools.chain(*(
		itertools.combinations(
			(
				'status',
				'chain',
				'created',
				'metadata'
			),
			n
		)
		for n in range(1, 5)
	))
)
@pydantic.validate_arguments
def test_get_exact(rows: Rows_, row: Row, query_all: ItemQuery, changed_row: Row):

	rows.add(row)
	rows.add(changed_row)

	assert len([*rows[query_all]]) == 2

	result = [*rows[
		ItemQuery(
			mask=ItemMask(
				type     = row.type,
				status   = row.status,
				chain    = Item.Chain(ref=row.chain),
				created  = row.created,
				metadata = row.metadata
			),
			limit=1
		)
	]]
	assert len(result) == 1
	assert result[0] == row