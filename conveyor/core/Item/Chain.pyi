import pydantic
from .Data import Data as Data

class Chain:
    ref: Data | pydantic.StrictStr
    test: str | None
    def test_valid(cls, test: str | None, values: dict[str, Data | pydantic.StrictStr]) -> str | None: ...
    @property
    def value(self) -> str: ...
    def __eq__(self, another: object) -> bool: ...
