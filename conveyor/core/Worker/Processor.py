import abc
import typing
import pydantic



S = typing.TypeVar('S')
T = typing.TypeVar('T')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Error(RuntimeError, typing.Generic[S]):
	input     : S
	exception : Exception


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Processor(typing.Generic[S, T], metaclass = abc.ABCMeta):

	Error = Error

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	@typing.final
	def error(self, i: S, exception: Exception) -> Error[S]:
		return Error(
			input     = i,
			exception = exception
		)

	@abc.abstractmethod
	def __call__(self, input: typing.Callable[[], typing.Iterable[S]], config: dict[str, typing.Any]) -> typing.Iterable[T]:
		pass