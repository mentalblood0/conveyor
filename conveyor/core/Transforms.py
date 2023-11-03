import abc
import typing
import dataclasses


S = typing.TypeVar("S")
T = typing.TypeVar("T")

S_ = typing.TypeVar("S_")
T_ = typing.TypeVar("T_")


@dataclasses.dataclass(frozen=True, kw_only=True)
class Transform(typing.Generic[S, T], abc.ABC):
    @abc.abstractmethod
    def transform(self, i: S) -> T:
        """"""

    @abc.abstractmethod
    def __call__(self, i: S) -> T:
        """"""

    @abc.abstractmethod
    def __invert__(self: "Transform[S, T]") -> "Transform[T, S]":
        """"""

    @typing.final
    def valid(self, i: S) -> bool:
        try:
            self(i)
            return True
        except Exception:
            return False

    @typing.final
    def __add__(self, another: "Transform[T, T_]") -> "_Transforms[S, T, T_]":
        return _Transforms(self, another)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Safe(Transform[S, T]):
    @typing.final
    def __call__(self, i: S) -> T:
        result = self.transform(i)

        if i != (inverted := (~self).transform(result)):
            raise TypeError(
                f"Transform `{self}` not invertible for input `{i}`"
                f": got `{(inverted)} instead`"
            )

        return result


@dataclasses.dataclass(frozen=True, kw_only=True)
class Trusted(Transform[S, T]):
    @typing.final
    def __call__(self, i: S) -> T:
        return self.transform(i)


M = typing.TypeVar("M")


@dataclasses.dataclass(frozen=True, kw_only=False)
class _Transforms(Trusted[S, T], typing.Generic[S, M, T]):
    first: "_Transforms[S, typing.Any, M]" | Transform[S, M]
    second: "_Transforms[M, typing.Any, T]" | Transform[M, T]

    def transform(self, i: S) -> T:
        return self.second(self.first(i))

    def __invert__(self) -> "_Transforms[T, M, S]":
        return _Transforms(~self.second, ~self.first)


@dataclasses.dataclass(frozen=True, kw_only=False)
class Nothing(Trusted[T, T], typing.Generic[T]):
    def __invert__(self) -> typing.Self:
        return self
