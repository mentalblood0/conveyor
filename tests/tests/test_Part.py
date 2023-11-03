import pytest

from conveyor.core.Item import Part

from ..common import *


@pytest.fixture
def part():
    return Part()


@pytest.mark.parametrize(
    "field",
    (
        "item",
        "kind",
        "status",
        "data",
        "digest",
        "metadata",
        "chain",
        "created",
        "reserver",
    ),
)
def test_none_fields(part: Part, field: str):
    with pytest.raises(KeyError):
        part.__getattribute__(field)
