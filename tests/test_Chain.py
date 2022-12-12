import pytest
import datetime
import pydantic
import dataclasses

from conveyor.core import Item

from .common import *



@pydantic.validate_arguments
def test_immutable(item: Item):
	with pytest.raises(dataclasses.FrozenInstanceError):
		item.value = 'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del item.value
	with pytest.raises(dataclasses.FrozenInstanceError):
		item.x = 'x'


@pydantic.validate_arguments
def test_chain_ref_is_data_or_item(item: Item):

	with pytest.raises(pydantic.ValidationError):
		Item.Chain(ref='lalala')

	Item.Chain(ref=item.data)


@pydantic.validate_arguments
def test_chain_equal(item: Item):
	assert Item.Chain(ref=item.data) == Item.Chain(ref=item.data)