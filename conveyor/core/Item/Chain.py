import dataclasses

from .Data import Data


@dataclasses.dataclass(frozen=True, kw_only=True)
class Chain:
    ref: Data | str
    test: str | None = None

    @property
    def value(self) -> str:
        match self.ref:
            case Data():
                return self.ref.digest.string
            case str():
                return self.ref

    def __eq__(self, another: object) -> bool:
        if not isinstance(another, Chain):
            raise TypeError(
                f"Can not compare instance of type `Chain` "
                f"with instance of type `{type(another)}`"
            )
        return self.value == another.value
