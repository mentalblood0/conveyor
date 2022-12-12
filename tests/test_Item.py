import pytest
import datetime
import pydantic
import dataclasses

from conveyor.core import Item

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
def test_immutable(item: Item):
	with pytest.raises(dataclasses.FrozenInstanceError):
		item.type = 'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del item.type
	with pytest.raises(dataclasses.FrozenInstanceError):
		item.x = 'x'


@pydantic.validate_arguments
def test_metadata_immutable(item: Item):
	with pytest.raises(TypeError):
		item.metadata.value[Item.Metadata.Key('a')] = 'b'
	with pytest.raises(TypeError):
		del item.metadata.value[Item.Metadata.Key('a')]
	with pytest.raises(TypeError):
		item.metadata.value[Item.Metadata.Key('b')] = 'b'