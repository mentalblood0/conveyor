import pytest
import typing
import datetime
import itertools
import dataclasses

from conveyor.repositories import Rows
from conveyor.core import Query, Mask, Item

from ..common import *



def test_append_get_delete(rows: Rows.Core, row: Rows.Core.Item, query_all: Query):

	rows.append(row)

	saved_items = [*rows[query_all]]
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
	assert not len([*rows[query_all]])


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


def test_delete_nonexistent(rows: Rows.Core, row: Rows.Core.Item):
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
				current = row.metadata[Item.Metadata.Key('key')]
				match current:
					case str():
						new = '_'
					case _:
						raise ValueError
				value = row.metadata | {Item.Metadata.Key('key'): new}
			case _:
				continue
		changes[key] = value

	return dataclasses.replace(row, **changes)


def test_add_columns_one(rows: Rows.Core, row: Rows.Core.Item):

	rows.append(row)
	assert [*rows[Query(
		mask  = Mask(type = row.type),
		limit = 1
	)]] == [row]

	new_metadata = row.metadata | {Item.Metadata.Key('new_column'): 'lalala'}
	new_row = dataclasses.replace(row, metadata = new_metadata)

	rows.append(new_row)
	assert [*rows[Query(
		mask = Mask(
			type = row.type,
			metadata = new_metadata
		),
		limit = 1
	)]] == [new_row]



def test_add_columns_many(rows: Rows.Core, row: Rows.Core.Item):
	rows.append(row)
	rows.append(dataclasses.replace(
		row,
		metadata = row.metadata | {
			Item.Metadata.Key('new_column_1'): 'lalala',
			Item.Metadata.Key('new_column_2'): 'lololo'
		}
	))


def test_contains(rows: Rows.Core, row: Rows.Core.Item):
	assert row not in rows
	rows.append(row)
	assert row in rows


def test_delete(rows: Rows.Core, row: Rows.Core.Item):
	rows.append(row)
	del rows[row]
	assert row not in rows


def test_len(rows: Rows.Core, row: Rows.Core.Item):
	assert not len(rows)
	for i in range(3):
		rows.append(row)
		assert len(rows) == i + 1


def test_extend_status_enum(rows: Rows.Core, row: Rows.Core.Item):

	changed_status = Item.Status(f'{row.status.value}_')
	changed_row = dataclasses.replace(row, status = changed_status)

	rows.append(row)
	rows.append(changed_row)

	assert [*rows[Query(
		mask  = Mask(type = row.type, status = row.status),
		limit = 2
	)]] == [row]
	assert [*rows[Query(
		mask  = Mask(type = row.type, status = changed_row.status),
		limit = 2
	)]] == [changed_row]


def test_extend_metadata_enum(rows: Rows.Core, row: Rows.Core.Item):

	metadata_1 = row.metadata | {Item.Metadata.Key('new_column'): Item.Metadata.Enumerable('lalala')}
	metadata_2 = row.metadata | {Item.Metadata.Key('new_column'): Item.Metadata.Enumerable('lololo')}

	item_1 = dataclasses.replace(row, metadata = metadata_1)
	item_2 = dataclasses.replace(row, metadata = metadata_2)

	rows.append(dataclasses.replace(row, metadata = metadata_1))
	rows.append(dataclasses.replace(row, metadata = metadata_2))

	assert [*rows[Query(
		mask  = Mask(type = row.type, metadata = metadata_1),
		limit = 2
	)]] == [item_1]
	assert [*rows[Query(
		mask  = Mask(type = row.type, metadata = metadata_2),
		limit = 2
	)]] == [item_2]


def test_none_metadata_enum_value(rows: Rows.Core, row: Rows.Core.Item):

	metadata_1 = row.metadata | {Item.Metadata.Key('new_column'): Item.Metadata.Enumerable('lalala')}
	metadata_2 = row.metadata | {Item.Metadata.Key('new_column'): Item.Metadata.Enumerable(None)}

	item_1 = dataclasses.replace(row, metadata = metadata_1)
	item_2 = dataclasses.replace(row, metadata = metadata_2)

	rows.append(dataclasses.replace(row, metadata = metadata_1))
	rows.append(dataclasses.replace(row, metadata = metadata_2))

	assert [*rows[Query(
		mask  = Mask(type = row.type, metadata = metadata_1),
		limit = 2
	)]] == [item_1]
	assert [*rows[Query(
		mask  = Mask(type = row.type, metadata = metadata_2),
		limit = 2
	)]] == [item_2]


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