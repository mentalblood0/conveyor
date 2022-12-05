import pytest
import pydantic
import dataclasses

from conveyor.core import Digest



def test_no_accept_non_bytes_value():
	with pytest.raises(pydantic.ValidationError):
		Digest(None)
	with pytest.raises(pydantic.ValidationError):
		Digest(32)
	with pytest.raises(pydantic.ValidationError):
		Digest(' ' * 32)


def test_no_accept_short_value():
	with pytest.raises(pydantic.ValidationError):
		Digest(b'')
	with pytest.raises(pydantic.ValidationError):
		Digest(b' ')
	with pytest.raises(pydantic.ValidationError):
		Digest(b' ' * 31)


def test_immutable():
	with pytest.raises(dataclasses.FrozenInstanceError):
		Digest(b' ' * 32).value = b'x' * 32
	with pytest.raises(dataclasses.FrozenInstanceError):
		del Digest(b' ' * 32).value
	with pytest.raises(dataclasses.FrozenInstanceError):
		Digest(b' ' * 32).x = b'x' * 32


def test_value():
	v = b' ' * 32
	assert Digest(v).value == v


def test_string():
	l = 32
	s = Digest(b' ' * 32).string
	assert len(s) > l


def test_path():

	p = Digest(b' ' * 32).path

	p.parent.mkdir(parents=True, exist_ok=True)
	p.touch(exist_ok=True)

	p.unlink()
	while len(p.parts) > 1:
		p = p.parent
		p.rmdir()


def test_equal():
	v = b' ' * 32
	assert Digest(v) == Digest(v)
	assert Digest(v) != Digest(b'x' * 32)
	assert Digest(v) != Digest(b' ' * 33)