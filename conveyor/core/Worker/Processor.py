import abc
import typing
import pydantic



S = typing.TypeVar('S')
T = typing.TypeVar('T')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Processor(typing.Generic[S, T], metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def __call__(self, input: typing.Callable[[], typing.Iterable[S]], config: dict[str, typing.Any]) -> typing.Iterable[T]:
		pass