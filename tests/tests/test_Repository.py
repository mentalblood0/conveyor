import typing
import pytest
import itertools
import dataclasses

from conveyor.core import Item, Query, Mask, Repository

from ..common import *



def test_append_get_delete(repository: Repository, item: Item, query_all: Query):

	repository.append(item)

	saved_items = [*repository[query_all]]
	assert len(saved_items) == 1
	saved = saved_items[0]
	assert saved.type == item.type
	assert saved.status == item.status
	assert saved.data == item.data
	assert saved.metadata == item.metadata
	assert saved.chain == item.chain
	assert saved.created == item.created
	assert saved.reserver.value is not None

	del repository[saved]
	assert not len([*repository[query_all]])


def test_delete_nonexistent(repository: Repository, item: Item):
	del repository[item]


def test_transaction_one(repository: Repository, item: Item):

	assert not len(repository)

	try:
		with repository.transaction() as t:
			t.append(item)
			raise KeyError
	except KeyError:
		assert not len(repository)

	with repository.transaction() as t:
		t.append(item)
	assert len(repository) == 1


def test_transaction_many(repository: Repository, item: Item):

	assert not len(repository)

	try:
		with repository.transaction() as t:
			for _ in range(3):
				t.append(item)
			raise KeyError
	except KeyError:
		assert not len(repository)

	with repository.transaction() as t:
		for _ in range(3):
			t.append(item)
	assert len(repository) == 3


@pytest.fixture
def changed_item(item: Item, changes_list: typing.Iterable[str]) -> Item:

	changes: dict[str, Item.Value | Item.Metadata | Item.Data] = {}

	for key in changes_list:
		value: Item.Value | Item.Metadata | Item.Data | None = None
		match key:
			case 'status':
				value = Item.Status('CHANGED')
			case 'chain':
				value = Item.Chain(ref=Item.Data(value=b'CHANGED'))
			case 'data':
				value = Item.Data(value=b'CHANGED')
			case 'created':
				value = Item.Created(item.created.value - datetime.timedelta(seconds=1))
			case 'metadata':
				current = item.metadata['key']
				match current:
					case Item.Metadata.Enumerable():
						new = Item.Metadata.Enumerable('CHANGED')
					case str():
						new = 'CHANGED'
					case _:
						raise ValueError
				value = item.metadata | {Item.Metadata.Key('key'): new}
			case _:
				continue
		changes[key] = value

	return dataclasses.replace(item, **changes)


@pytest.mark.parametrize(
	'changes_list',
	(
		c for c in itertools.chain(*(
			itertools.combinations(
				(
					'status',
					'chain',
					'data',
					'created',
					'metadata'
				),
				n
			)
			for n in range(1, 6)
		))
		if not (('chain' in c and 'data' not in c) or ('chain' not in c and 'data' in c))
	)
)
def test_get_exact(repository: Repository, item: Item, query_all: Query, changed_item: Item):

	repository.append(item)
	repository.append(changed_item)

	both = [*repository[query_all]]
	assert len(both) == 2
	for i in both:
		repository[i] = i

	result = [*repository[
		Query(
			mask=Mask(
				type     = item.type,
				status   = item.status,
				chain    = item.chain,
				data     = item.data,
				created  = item.created,
				metadata = item.metadata
			),
			limit=None
		)
	]]
	assert len(result) == 1
	assert result[0] == item

	for i in repository[query_all]:
		del repository[i]