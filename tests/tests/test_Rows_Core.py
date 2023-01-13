import pytest
import typing
import datetime
import pydantic
import itertools
import dataclasses

from conveyor.repositories import Rows
from conveyor.core import Query, Mask, Item

from ..common import *



@pytest.fixture
def row() -> Rows.Core.Item:

	data = Item.Data(value=b'')

	return Rows.Core.Item(
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
def query_all(row: Rows.Core.Item) -> Query:
	return Query(
		mask=Mask(
			type=row.type
		),
		limit=128
	)


@pydantic.validate_arguments
def test_immutable(rows: Rows.Core):
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.__setattr__('db', b'x')
	with pytest.raises(dataclasses.FrozenInstanceError):
		del rows.db
	with pytest.raises(dataclasses.FrozenInstanceError):
		rows.__setattr__('x', b'x')


@pydantic.validate_arguments
def test_append_get_delete(rows: Rows.Core, row: Rows.Core.Item):

	rows.append(row)

	query = Query(
		mask=Mask(
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
def test_transaction_append_one_in_one_table(rows: Rows.Core, row: Rows.Core.Item):

	try:
		with rows.transaction() as t:
			t.append(row)
			assert len(t) == 1
			raise KeyError
	except KeyError:
		assert not len(rows)

	with rows.transaction() as t:
		t.append(row)
		assert len(t) == 1
	assert len(rows) == 1


@pydantic.validate_arguments
def test_transaction_append_many_in_one_table(rows: Rows.Core, row: Rows.Core.Item):

	try:
		with rows.transaction() as t:
			for _ in range(3):
				t.append(row)
			assert len(t) == 3
			raise KeyError
	except KeyError:
		assert not len(rows)

	with rows.transaction() as t:
		for _ in range(3):
			t.append(row)
		assert len(t) == 3
	assert len(rows) == 3


@pydantic.validate_arguments
def test_transaction_append_one_in_many_tables(rows: Rows.Core, row: Rows.Core.Item):

	another_row = dataclasses.replace(
		row,
		type=Item.Type('another_type')
	)

	try:
		with rows.transaction() as t:
			t.append(row)
			t.append(another_row)
			assert len(t) == 2
			raise KeyError
	except KeyError:
		assert not len(rows)

	with rows.transaction() as t:
		t.append(row)
		t.append(another_row)
		assert len(t) == 2
	assert len(rows) == 2


@pydantic.validate_arguments
def test_delete_nonexistent(rows: Rows.Core, row: Rows.Core.Item):
	with pytest.raises(KeyError):
		del rows[row]


@pytest.fixture
def changed_row(row: Rows.Core.Item, changes_list: typing.Iterable[str]) -> Rows.Core.Item:

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


@pydantic.validate_arguments
def test_add_column(rows: Rows.Core, row: Rows.Core.Item):
	rows.append(row)
	rows.append(dataclasses.replace(
		row,
		metadata = Item.Metadata(row.metadata.value | {Item.Metadata.Key('new_column'): 'lalala'})
	))


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
def test_get_exact(rows: Rows.Core, row: Rows.Core.Item, query_all: Query, changed_row: Rows.Core.Item):

	rows.append(row)
	rows.append(changed_row)

	assert len([*rows[query_all]]) == 2

	result = [*rows[
		Query(
			mask=Mask(
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

	for r in [*rows[query_all]]:
		del rows[r]