import typing
import pydantic
import functools
import dataclasses



O = typing.TypeVar('O')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Transform(typing.Generic[O]):

	inverted: bool = False
	test:     bool = True

	def direct(self, o: O) -> O:
		raise NotImplementedError

	def inverse(self, o: O) -> O:
		raise NotImplementedError

	@pydantic.validate_arguments
	def __call__(self, o: O) -> O:

		result: O | None = None
		if self.inverted:
			result = self.inverse(o)
		else:
			result = self.direct(o)

		if self.test:

			test: O | None = None
			if self.inverted:
				test = self.direct(result)
			else:
				test = self.inverse(result)

			if o != test:
				raise ValueError(f'Transform {self} not invertible for object {o}')

		return result

	def __invert__(self) -> typing.Self:
		return dataclasses.replace(self, inverted = not self.inverted)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transforms(Transform[O]):

	Transform = Transform

	sequence: typing.Sequence[Transform[O]] = ()
	test: bool = False

	@pydantic.validate_arguments
	def direct(self, o: O) -> O:
		return functools.reduce(
			lambda result, t: t(result),
			self.sequence,
			o
		)

	@pydantic.validate_arguments
	def inverse(self, o: O) -> O:
		return functools.reduce(
			lambda result, t: (~t)(result),
			reversed(self.sequence),
			o
		)

	def __invert__(self) -> typing.Self:
		return Transforms(
			sequence = [
				~t
				for t in reversed(self.sequence)
			]
		)