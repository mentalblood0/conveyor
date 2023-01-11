import typing
import pydantic



I = typing.TypeVar('I')
O = typing.TypeVar('O')


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