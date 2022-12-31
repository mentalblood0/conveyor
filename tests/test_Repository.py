import typing
import pytest
import pathlib
import pydantic
import itertools
import sqlalchemy
import dataclasses

from conveyor.repositories.Rows import Rows
from conveyor.repositories.Files import Files
from conveyor.core import Item, Query, Mask, Repository

from .common import *


@pytest.fixture
@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def repository(db: sqlalchemy.Engine) -> Repository:
	return Repository([
		Rows(Rows.Core(db)),
		Files(Files.Core(root=pathlib.Path('tests/files'), suffix='.txt'))
	])


@pytest.fixture
@pydantic.validate_arguments
def query_all(item: Item) -> Query:
	return Query(
		mask=Mask(
			type=item.type
		),
		limit=128
	)


@pydantic.validate_arguments
def test_immutable(repository: Repository):
	with pytest.raises(dataclasses.FrozenInstanceError):
		repository.__setattr__('parts', b'x')
	with pytest.raises(dataclasses.FrozenInstanceError):
		del repository.parts
	with pytest.raises(dataclasses.FrozenInstanceError):
		repository.__setattr__('x', b'x')


@pydantic.validate_arguments
def test_append_get_delete(repository: Repository, item: Item):

	repository.add(item)

	query = Query(
		mask=Mask(
			type=item.type
		),
		limit=128
	)
	saved_items = [*repository[query]]
	assert len(saved_items) == 1
	saved = saved_items[0]
	assert saved.type == item.type
	assert saved.status == item.status
	assert saved.data == item.data
	assert saved.metadata == item.metadata
	assert saved.chain == item.chain
	assert saved.created == item.created
	assert saved.reserver.exists

	del repository[saved]
	assert not len([*repository[query]])


@pydantic.validate_arguments
def test_delete_nonexistent(repository: Repository, item: Item):
	del repository[item]


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
				current = item.metadata.value[Item.Metadata.Key('key')]
				match current:
					case str():
						new = 'CHANGED'
					case _:
						raise ValueError
				value = Item.Metadata(item.metadata.value | {Item.Metadata.Key('key'): new})
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
@pydantic.validate_arguments
def test_get_exact(repository: Repository, item: Item, query_all: Query, changed_item: Item):

	repository.add(item)
	repository.add(changed_item)

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
			limit=128
		)
	]]
	assert len(result) == 1
	assert result[0] == item

	for i in repository[query_all]:
		del repository[i]