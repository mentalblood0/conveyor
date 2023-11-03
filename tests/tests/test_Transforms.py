import enum
import pytest
import typing
import dataclasses

from conveyor.core import Transforms

from ..common import *


def test_nothing_transform():
    assert Transforms.Nothing[str]()("string") == "string"


def test_transform_not_invertible_by_default():
    @dataclasses.dataclass(frozen=True, kw_only=False)
    class Test(Transforms.Safe[str, str]):
        def transform(self, i: str) -> str:
            return i

    with pytest.raises(NotImplementedError):
        assert Test()("string")
