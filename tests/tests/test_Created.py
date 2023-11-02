import pytest
import datetime

from conveyor.core.Item import Created


def test_checking_value():
    with pytest.raises(ValueError):
        Created(datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=1))

    Created(datetime.datetime.now(datetime.UTC))
