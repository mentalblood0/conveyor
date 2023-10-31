import dataclasses

from .Data import Data


@dataclasses.dataclass(frozen=True, kw_only=True)
class Chain:
    ref: Data | str
    test: str | None = None

    def __post_init__(self):
        if self.test is not None:
            match self.ref:
                case Data():
                    correct = Chain(ref=self.ref).value
                case str():
                    correct = self.ref

            if correct != self.test:
                raise ValueError(
                    f'Provided chain value "{self.test}" is not correct '
                    f'(correct is "{correct}")'
                )

    @property
    def value(self) -> str:
        match self.ref:
            case Data():
                return self.ref.digest.string
            case str():
                return self.ref

    def __eq__(self, another: object) -> bool:
        match another:
            case Chain():
                return self.value == another.value
            case _:
                raise ValueError(
                    f"Can not compare instance of type `Chain` "
                    f"with instance of type `{type(another)}`"
                )
