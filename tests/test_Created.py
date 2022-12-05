import pytest
import datetime
import pydantic
import dataclasses

from conveyor.core import Created



def test_value_is_datetime():

	with pytest.raises(pydantic.ValidationError):
		Created('lalala')
	with pytest.raises(pydantic.ValidationError):
		Created(1234)

	Created(datetime.datetime.utcnow())


def test_checking_value():

	with pytest.raises(pydantic.ValidationError):
		Created(datetime.datetime.utcnow() + datetime.timedelta(minutes=1))

	Created(datetime.datetime.utcnow())


def test_immutable():
	with pytest.raises(dataclasses.FrozenInstanceError):
		Created(datetime.datetime.utcnow()).value = b'x' * 32
	with pytest.raises(dataclasses.FrozenInstanceError):
		del Created(datetime.datetime.utcnow()).value
	with pytest.raises(dataclasses.FrozenInstanceError):
		Created(datetime.datetime.utcnow()).x = b'x' * 32