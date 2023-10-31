import abc
import typing
import dataclasses


S = typing.TypeVar("S")
T = typing.TypeVar("T")


@dataclasses.dataclass(frozen=True, kw_only=True)
class Error(RuntimeError, typing.Generic[S]):
    input: S
    exception: Exception


@dataclasses.dataclass(frozen=True, kw_only=True)
class Processor(typing.Generic[S, T], metaclass=abc.ABCMeta):
    Error = Error

    @typing.final
    def error(self, i: S, exception: Exception) -> Error[S]:
        return Error(input=i, exception=exception)

    @abc.abstractmethod
    def __call__(
        self, input: typing.Callable[[], typing.Iterable[S]], config: typing.Any
    ) -> typing.Iterable[T]:
        pass
