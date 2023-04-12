import pydantic
import typing
from .Digest import Digest as Digest

def default_algorithm(input_: bytes) -> bytes: ...

class Data:
    Digest = Digest
    value: pydantic.StrictBytes
    test: Digest | None
    algorithm: typing.Callable[[bytes], bytes]
    def test_valid(cls, test: Digest | None, values: dict[str, pydantic.StrictBytes]) -> Digest | None: ...
    @property
    def digest(self) -> Digest: ...
    @property
    def string(self) -> str: ...
