import re
import dataclasses

from .Enumerable import Enumerable


@dataclasses.dataclass(frozen=True, kw_only=False)
class Word(Enumerable):
    value: str

    regex = re.compile(r"\w+")

    def __post_init__(self):
        if not self.regex.fullmatch(self.value):
            raise TypeError(f"`Word` value must match regex {self.regex}")
