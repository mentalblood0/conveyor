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


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Transforms(Transform[I, O]):

	Transform = Transform

	sequence: tuple['Transforms[I, typing.Any]', 'Transforms[typing.Any, O]']

	@pydantic.validate_arguments
	def transform(self, i: I) -> O:
		return self.sequence[1](self.sequence[0](i))

	def __invert__(self) -> 'Transforms[O, I]':
		return Transforms((~self.sequence[1], ~self.sequence[0]))