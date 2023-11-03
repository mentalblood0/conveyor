import abc
import typing
import dataclasses


S = typing.TypeVar("S")
T = typing.TypeVar("T")


@dataclasses.dataclass(frozen=True, kw_only=True)
class Error(RuntimeError, typing.Generic[S]):
    payload: S
    exception: Exception


@dataclasses.dataclass(frozen=True, kw_only=True)
class Processor(typing.Generic[S, T], abc.ABC):
    Error = Error

    @typing.final
    def error(self, i: S, exception: Exception) -> Error[S]:
        return Error(payload=i, exception=exception)

    @abc.abstractmethod
    def __call__(
        self, payload: typing.Callable[[], typing.Iterable[S]], config: typing.Any
    ) -> typing.Iterable[T]:
        """"""
