from conveyor.core import Item

from ..common import *


def test_chain_equal_self(item: Item):
    assert Item.Chain(ref=item.data) == Item.Chain(ref=item.data)


def test_chain_not_equal_not_chain(item: Item):
    with pytest.raises(TypeError):
        assert Item.Chain(ref=item.data) == "something"
