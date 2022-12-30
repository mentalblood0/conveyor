import pytest

from conveyor.core.Item import Data, Digest



def test_checking_digest():
	with pytest.raises(ValueError):
		Data(value=b' ', test=Digest(b' ' * 32))


def test_value():
	v = b' '
	assert Data(value=v).value == v


def test_string():
	v = b' '
	assert Data(value=v).string == v.decode()


def test_equal():
	v = b' '
	assert Data(value=v) == Data(value=v)
	assert Data(value=v) != Data(value=b'x')
	assert Data(value=v) != Data(value=b'  ')