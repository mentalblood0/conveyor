import pytest
import datetime
import pydantic
import dataclasses

from conveyor.core import Created



def test_value_is_datetime():

	with pytest.raises(pydantic.ValidationError):
		Created(value='lalala')
	with pytest.raises(pydantic.ValidationError):
		Created(value=1234)

	Created(value=datetime.datetime.utcnow())


def test_checking_value():

	with pytest.raises(ValueError):
		Created(value=datetime.datetime.utcnow() + datetime.timedelta(minutes=1))

	Created(value=datetime.datetime.utcnow())


def test_immutable():
	with pytest.raises(dataclasses.FrozenInstanceError):
		Created(value=datetime.datetime.utcnow()).value = b'x' * 32
	with pytest.raises(dataclasses.FrozenInstanceError):
		del Created(value=datetime.datetime.utcnow()).value
	with pytest.raises(dataclasses.FrozenInstanceError):
		Created(value=datetime.datetime.utcnow()).x = b'x' * 32