import pytest
import pydantic
import dataclasses

from conveyor.core.Item import Data, Digest



def test_no_accept_non_bytes_value():
	with pytest.raises(pydantic.ValidationError):
		Data(value=None)
	with pytest.raises(pydantic.ValidationError):
		Data(value=32)
	with pytest.raises(pydantic.ValidationError):
		Data(value=' ')


def test_immutable():
	with pytest.raises(dataclasses.FrozenInstanceError):
		Data(value=b' ').value = b'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del Data(value=b' ').value
	with pytest.raises(dataclasses.FrozenInstanceError):
		Data(value=b' ').x = b'x'


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