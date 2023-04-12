import abc
import typing
from _typeshed import Incomplete

S: Incomplete
T: Incomplete

class Error(RuntimeError):
    input: S
    exception: Exception

class Processor(metaclass=abc.ABCMeta):
    Error = Error
    def error(self, i: S, exception: Exception) -> Error[S]: ...
    @abc.abstractmethod
    def __call__(self, input: typing.Callable[[], typing.Iterable[S]], config: dict[str, typing.Any]) -> typing.Iterable[T]: ...
