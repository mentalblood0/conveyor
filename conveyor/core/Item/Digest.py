import base64
import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=False)
class Digest:
    value: bytes

    @classmethod
    def from_base64(cls, source: str):
        return Digest(base64.b64decode(source.encode("ascii")))

    def __post_init__(self):
        if (given := len(self.value)) < (required := 32):
            raise TypeError(
                f"`Digest` value must be of minimum length {required} "
                f"(got {self.value} which is of length {given})"
            )

    @property
    def string(self) -> str:
        return base64.b64encode(self.value).decode("ascii")

    def __eq__(self, another: object) -> bool:
        if not isinstance(another, Digest):
            raise TypeError(
                "Can not compare instance of type `Digest` "
                f"with instance of type `{type(another)}`"
            )
        return self.value == another.value
