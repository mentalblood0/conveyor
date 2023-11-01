import re
import dataclasses

from .Enumerable import Enumerable


@dataclasses.dataclass(frozen=True, kw_only=False)
class Word(Enumerable):
    value: str

    def __post_init__(self):
        assert re.fullmatch(r"\w+", self.value), "`Word` value must be word"
