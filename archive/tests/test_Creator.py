import pytest

from conveyor.core import Item, Creator

from .common import *



type = 'undefined'
status = 'created'


@pytest.fixture
def item():
	return Item(
		type=type,
		status=status,
		data='lalala',
		metadata={
			'a': 1,
			'b': 2
		}
	)


def composeCreator(**kwargs):

	class DefaultCreator(Creator):

		def create(self, data, metadata):
			return Item(
				data=data,
				metadata=metadata
			)

	result = DefaultCreator(repository)
	for k, v in kwargs.items():
		setattr(result, k, v)

	return result


@pytest.fixture(autouse=True)
def clearDb():
	repository._drop(type)
	repository._drop('new')


def test_create_simple(item):

	assert composeCreator(
		output_type=type,
		output_status=status
	)(
		data=item.data,
		metadata=item.metadata
	)

	result = repository.get('undefined', where={'status': 'created'})[0]
	print(result)
	assert result.data == item.data
	assert result.metadata | item.metadata == item.metadata


def test_create_using_source(item):

	composeCreator(
		output_type=type,
		output_status=status,
	)(
		data='',
		metadata=item.metadata
	)
	source = repository.get(type)[0]

	composeCreator(
		output_type='new',
		output_status='created',
		source_type=type,
		source_status=status,
		match_fields=[*item.metadata.keys()]
	)(
		data=item.data,
		metadata=item.metadata
	)

	result = repository.get('new')[0]
	assert result.chain_id == source.chain_id