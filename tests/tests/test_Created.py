import pytest
import datetime
import pydantic

from conveyor.core.Item import Created



def test_checking_value():

	with pytest.raises(pydantic.ValidationError):
		Created(datetime.datetime.utcnow() + datetime.timedelta(minutes=1))

	Created(datetime.datetime.utcnow())