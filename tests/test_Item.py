import pytest
import datetime
import pydantic
import dataclasses

from conveyor.core import Chain, Item

from .common import *



@pydantic.validate_arguments
def test_type_is_word(item: Item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, type=b'lalala')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, type='')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, type='+')

	dataclasses.replace(item, type=Item.Type('l'))
	dataclasses.replace(item, type=Item.Type('lalala'))


@pydantic.validate_arguments
def test_status_is_word(item: Item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, status=b'lalala')
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, status=Item.Status(''))
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, status=Item.Status('+'))

	dataclasses.replace(item, status=Item.Status('l'))
	dataclasses.replace(item, status=Item.Status('lalala'))


@pydantic.validate_arguments
def test_metadata_is_metadata(item: Item):

	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, metadata=Item.Metadata({Item.Metadata.Key('a'): b''}))
	with pytest.raises(pydantic.ValidationError):
		dataclasses.replace(item, metadata=Item.Metadata({Item.Metadata.Key('a'): {}}))

	dataclasses.replace(item, metadata=Item.Metadata({Item.Metadata.Key('a'): 'str'}))
	dataclasses.replace(item, metadata=Item.Metadata({Item.Metadata.Key('a'): 1}))
	dataclasses.replace(item, metadata=Item.Metadata({Item.Metadata.Key('a'): 1.0}))
	dataclasses.replace(item, metadata=Item.Metadata({Item.Metadata.Key('a'): datetime.datetime.utcnow()}))


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
		item.metadata.value['a'] = 'b'
	with pytest.raises(TypeError):
		del item.metadata.value['a']
	with pytest.raises(TypeError):
		item.metadata.value['b'] = 'b'