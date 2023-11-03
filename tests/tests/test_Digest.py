import pytest

from conveyor.core.Item import Digest


def test_value():
    v = b" " * 32
    assert Digest(v).value == v


def test_invalid_value():
    with pytest.raises(TypeError):
        Digest(b" " * 31)


def test_string():
    length = 32
    s = Digest(b" " * 32).string
    assert len(s) > length


def test_equal_same():
    v = b" " * 32
    assert Digest(v) == Digest(v)


def test_not_equal_another_with_equal_length():
    assert Digest(b" " * 32) != Digest(b"x" * 32)


def test_not_equal_another_with_another_length():
    assert Digest(b" " * 32) != Digest(b" " * 33)


def test_not_equal_not_digest():
    with pytest.raises(TypeError):
        assert Digest(b" " * 32) == "lalala"
