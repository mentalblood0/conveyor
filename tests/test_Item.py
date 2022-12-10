import pytest
import datetime
import pydantic
import dataclasses

from conveyor.core import Data, Item, Chain, Created, Word



@pytest.fixture
def item() -> Item:

	data = Data(value=b'')

	return Item(
		type=Word('type'),
		status=Word('status'),
		data=data,
		metadata=Item.Metadata({Word('a'): 'a'}),
		chain=Chain(ref=data),
		created=Created(value=datetime.datetime.utcnow()),
		reserved=False,
		reserver=None
	)


@pydantic.validate_arguments
def test_type_is_word(item: Item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, type=b'lalala')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, type='')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, type='+')

	dataclasses.replace(item, type=Word('l'))
	dataclasses.replace(item, type=Word('lalala'))


@pydantic.validate_arguments
def test_status_is_word(item: Item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, status=b'lalala')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, status=Word(''))
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, status=Word('+'))

	dataclasses.replace(item, status=Word('l'))
	dataclasses.replace(item, status=Word('lalala'))


@pydantic.validate_arguments
def test_metadata_is_metadata(item: Item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, metadata=Item.Metadata({Word('a'): b''}))
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, metadata=Item.Metadata({Word('a'): {}}))

	dataclasses.replace(item, metadata=Item.Metadata({Word('a'): 'str'}))
	dataclasses.replace(item, metadata=Item.Metadata({Word('a'): 1}))
	dataclasses.replace(item, metadata=Item.Metadata({Word('a'): 1.0}))
	dataclasses.replace(item, metadata=Item.Metadata({Word('a'): datetime.datetime.utcnow()}))


@pydantic.validate_arguments
def test_chain_ref_is_data_or_item(item: Item):

	with pytest.raises(pydantic.ValidationError):
		Chain(ref='lalala')

	Chain(ref=item.data)
	Chain(ref=item)


@pydantic.validate_arguments
def test_chain_equal(item: Item):
	assert Chain(ref=item.data) == Chain(ref=item)


@pydantic.validate_arguments
def test_immutable(item: Item):
	with pytest.raises(dataclasses.FrozenInstanceError):
		item.type = 'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del item.value
	with pytest.raises(dataclasses.FrozenInstanceError):
		item.x = 'x'


@pydantic.validate_arguments
def test_metadata_immutable(item: Item):
	with pytest.raises(TypeError):
		item.metadata['a'] = 'b'
	with pytest.raises(TypeError):
		del item.metadata['a']
	with pytest.raises(TypeError):
		item.metadata['b'] = 'b'