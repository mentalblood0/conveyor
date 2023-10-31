from conveyor.core import Item

from ..common import *


def test_chain_equal(item: Item):
    assert Item.Chain(ref=item.data) == Item.Chain(ref=item.data)
