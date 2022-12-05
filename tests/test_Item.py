import pytest
import datetime
import pydantic
import frozendict
import dataclasses

from conveyor.core import Data, Item, Chain, Created, Word



@pytest.fixture
def valid_item():

	data = Data(value=b'')

	return Item(
		type=Word(value='type'),
		status=Word(value='status'),
		data=data,
		metadata=Item.Metadata(value={Word(value='a'): 'a'}),
		chain=Chain(ref=data),
		created=Created(value=datetime.datetime.utcnow()),
		reserved=None
	)


def test_type_is_word(valid_item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, type=b'lalala')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, type='')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, type='+')

	dataclasses.replace(valid_item, type=Word(value='l'))
	dataclasses.replace(valid_item, type=Word(value='lalala'))


def test_status_is_word(valid_item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, status=b'lalala')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, status=Word(value=''))
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, status=Word(value='+'))

	dataclasses.replace(valid_item, status=Word(value='l'))
	dataclasses.replace(valid_item, status=Word(value='lalala'))


def test_metadata_is_metadata(valid_item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, metadata=Item.Metadata(value={Word(value='a'): b''}))
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(valid_item, metadata=Item.Metadata(value={Word(value='a'): {}}))

	dataclasses.replace(valid_item, metadata=Item.Metadata(value={Word(value='a'): 'str'}))
	dataclasses.replace(valid_item, metadata=Item.Metadata(value={Word(value='a'): 1}))
	dataclasses.replace(valid_item, metadata=Item.Metadata(value={Word(value='a'): 1.0}))
	dataclasses.replace(valid_item, metadata=Item.Metadata(value={Word(value='a'): datetime.datetime.utcnow()}))


def test_chain_ref_is_data_or_item(valid_item):

	with pytest.raises(pydantic.ValidationError):
		Chain(ref='lalala')

	Chain(ref=valid_item.data)
	Chain(ref=valid_item)


def test_chain_equal(valid_item):
	assert Chain(ref=valid_item.data) == Chain(ref=valid_item)


def test_immutable(valid_item):
	with pytest.raises(dataclasses.FrozenInstanceError):
		valid_item.type = 'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del valid_item.value
	with pytest.raises(dataclasses.FrozenInstanceError):
		valid_item.x = 'x'


def test_metadata_immutable(valid_item):
	with pytest.raises(TypeError):
		valid_item.metadata['a'] = 'b'
	with pytest.raises(TypeError):
		del valid_item.metadata['a']
	with pytest.raises(TypeError):
		valid_item.metadata['b'] = 'b'