import datetime
import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=False)
class Created:
    value: datetime.datetime

    def __post_init__(self):
        if self.value > datetime.datetime.now(datetime.UTC):
            raise ValueError("`Created` value must not be greater then now")
