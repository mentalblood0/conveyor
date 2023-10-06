import pytest
import datetime

from conveyor.core.Item import Created



def test_checking_value():

	with pytest.raises(ValueError):
		Created(datetime.datetime.utcnow() + datetime.timedelta(minutes=1))

	Created(datetime.datetime.utcnow())