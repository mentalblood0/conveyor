import datetime
import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=False)
class Created:
    value: datetime.datetime

    def __post_init__(self):
        assert self.value <= (
            now := datetime.datetime.now(datetime.UTC)
        ), f"`Created` value {self.value} must not be greater then now {now}"
