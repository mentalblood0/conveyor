import pytest
import dataclasses

from conveyor.core import Transforms
from conveyor.core.Transforms import Transform

from ..common import *


def test_nothing_transform(
    nothing: Transforms.Trusted[str, str] = Transforms.Nothing[str](),
):
    assert nothing("string") == "string"
    assert ~nothing == nothing


def test_transform_combination():
    double_nothing = Transforms.Nothing[str]() + Transforms.Nothing[str]()
    test_nothing_transform(double_nothing)


def test_transform_not_invertible_by_default():
    @dataclasses.dataclass(frozen=True, kw_only=False)
    class Test(Transforms.Safe[str, str]):
        def transform(self, i: str) -> str:
            return i

    with pytest.raises(NotImplementedError):
        Test()("string")


def test_safe_transform_checks_inverted():
    @dataclasses.dataclass(frozen=True, kw_only=False)
    class Test(Transforms.Safe[str, str]):
        def transform(self, i: str) -> str:
            return i + "postfix"

        def __invert__(self: Transform[str, str]) -> Transform[str, str]:
            return self

    with pytest.raises(TypeError):
        Test()("string")


def test_trusted_transform_does_not_check_inverted():
    @dataclasses.dataclass(frozen=True, kw_only=False)
    class Test(Transforms.Trusted[str, str]):
        def transform(self, i: str) -> str:
            return i + "postfix"

    Test()("string")
