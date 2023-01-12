import typing
import pydantic



I = typing.TypeVar('I')
O = typing.TypeVar('O')

I_ = typing.TypeVar('I_')
O_ = typing.TypeVar('O_')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transform(typing.Generic[I, O]):

	test: bool = True

	def transform(self, i: I) -> O:
		raise NotImplementedError

	@pydantic.validate_arguments
	def __call__(self, i: I) -> O:

		result = self.transform(i)

		if self.test:
			inverted = ~self
			if i != inverted.transform(result):
				raise ValueError(f'Transform `{self}` not invertible for input `{i}`')

		return result

	def __invert__(self: 'Transform[I, O]') -> 'Transform[O, I]':
		raise NotImplementedError

	def __add__(self, another: 'Transform[O, O_]') -> 'Transforms[I, O, O_]':
		return Transforms(self, another)


M = typing.TypeVar('M')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Transforms(Transform[I, O], typing.Generic[I, M, O]):

	Transform = Transform

	first:  'Transforms[I, typing.Any, M]' | Transform[I, M]
	second: 'Transforms[M, typing.Any, O]' | Transform[M, O]

	@pydantic.validate_arguments
	def transform(self, i: I) -> O:
		return self.second(self.first(i))

	def __invert__(self) -> 'Transforms[O, M, I]':
		return Transforms(~self.second, ~self.first)

	def __add__(self, another: 'Transforms[O, typing.Any, O_]' | Transform[O, O_]) -> 'Transforms[I, O, O_]':
		return Transforms(self, another)

	def __radd__(self, another: 'Transforms[I_, typing.Any, I]' | Transform[I_, I]) -> 'Transforms[I_, I, O]':
		return Transforms(another, self)