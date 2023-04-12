import datetime

class Created:
    value: datetime.datetime
    def value_valid(cls, value: datetime.datetime) -> datetime.datetime: ...
