import abc
import typing
import pydantic



S = typing.TypeVar('S')
T = typing.TypeVar('T')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Processor(typing.Generic[S, T], metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def error(self, i: S, exception: Exception) -> typing.Iterable[T]:
		pass

	@abc.abstractmethod
	def _handle(self, i: S, other: typing.Iterable[S], config: dict[str, typing.Any]) -> typing.Iterable[T]:
		pass

	@pydantic.validate_arguments
	@typing.final
	def handle(self, i: S, other: typing.Iterable[S], config: dict[str, typing.Any]) -> typing.Iterable[T]:
		try:
			for a in self._handle(i, other, config):
				yield a
		except Exception as exception:
			for e in self.error(i, exception):
				yield e

	@abc.abstractmethod
	def __call__(self, input: typing.Callable[[], typing.Iterable[S]], config: dict[str, typing.Any]) -> typing.Iterable[T]:
		pass