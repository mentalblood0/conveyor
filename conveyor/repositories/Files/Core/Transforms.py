import abc
import typing
import pydantic



I = typing.TypeVar('I')
O = typing.TypeVar('O')

I_ = typing.TypeVar('I_')
O_ = typing.TypeVar('O_')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transform(typing.Generic[I, O], metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def transform(self, i: I) -> O:
		pass

	@abc.abstractmethod
	def __call__(self, i: I) -> O:
		pass

	@abc.abstractmethod
	def __invert__(self: 'Transform[I, O]') -> 'Transform[O, I]':
		pass

	def __add__(self, another: 'Transform[O, O_]') -> '_Transforms[I, O, O_]':
		return _Transforms(self, another)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Safe(Transform[I, O]):

	@pydantic.validate_arguments
	def __call__(self, i: I) -> O:

		result = self.transform(i)

		if i != (~self).transform(result):
			raise ValueError(f'Transform `{self}` not invertible for input `{i}`')

		return result


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Trusted(Transform[I, O]):

	@pydantic.validate_arguments
	def __call__(self, i: I) -> O:
		return self.transform(i)


M = typing.TypeVar('M')

@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class _Transforms(Trusted[I, O], typing.Generic[I, M, O]):

	first:  '_Transforms[I, typing.Any, M]' | Transform[I, M]
	second: '_Transforms[M, typing.Any, O]' | Transform[M, O]

	@pydantic.validate_arguments
	def transform(self, i: I) -> O:
		return self.second(self.first(i))

	def __invert__(self) -> '_Transforms[O, M, I]':
		return _Transforms(~self.second, ~self.first)

	def __add__(self, another: '_Transforms[O, typing.Any, O_]' | Transform[O, O_]) -> '_Transforms[I, O, O_]':
		return _Transforms(self, another)

	def __radd__(self, another: '_Transforms[I_, typing.Any, I]' | Transform[I_, I]) -> '_Transforms[I_, I, O]':
		return _Transforms(another, self)