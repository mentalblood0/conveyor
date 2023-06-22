import abc
import typing
import pydantic



S = typing.TypeVar('S')
T = typing.TypeVar('T')

S_ = typing.TypeVar('S_')
T_ = typing.TypeVar('T_')


@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Transform(typing.Generic[S, T], metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def transform(self, i: S) -> T:
		pass

	@abc.abstractmethod
	def __call__(self, i: S) -> T:
		pass

	@abc.abstractmethod
	def __invert__(self: 'Transform[S, T]') -> 'Transform[T, S]':
		pass

	@typing.final
	def valid(self, i: S) -> bool:
		try:
			self(i)
			return True
		except:
			return False

	@typing.final
	def __add__(self, another: 'Transform[T, T_]') -> '_Transforms[S, T, T_]':
		return _Transforms(self, another)

	@typing.final
	def __radd__(self, another: 'Transform[S_, S]') -> '_Transforms[S_, S, T]':
		return _Transforms(another, self)


@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Safe(Transform[S, T]):

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, i: S) -> T:

		result = self.transform(i)

		if i != (inverted := (~self).transform(result)):
			raise ValueError(f'Transform `{self}` not invertible for input `{i}`: got `{(inverted)} instead`')

		return result


@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Trusted(Transform[S, T]):

	@pydantic.validate_arguments
	@typing.final
	def __call__(self, i: S) -> T:
		return self.transform(i)


M = typing.TypeVar('M')

@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class _Transforms(Trusted[S, T], typing.Generic[S, M, T]):

	first:  '_Transforms[S, typing.Any, M]' | Transform[S, M]
	second: '_Transforms[M, typing.Any, T]' | Transform[M, T]

	@pydantic.validate_arguments
	def transform(self, i: S) -> T:
		return self.second(self.first(i))

	def __invert__(self) -> '_Transforms[T, M, S]':
		return _Transforms(~self.second, ~self.first)