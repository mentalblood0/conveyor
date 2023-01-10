import typing
import pydantic
import functools
import dataclasses

from ...core.Item import Data



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Transform:

	inverted: bool = False
	test:     bool = True

	def direct(self, data: Data) -> Data:
		raise NotImplementedError

	def inverse(self, data: Data) -> Data:
		raise NotImplementedError

	@pydantic.validate_arguments
	def __call__(self, data: Data) -> Data:

		result: Data | None = None
		if self.inverted:
			result = self.inverse(data)
		else:
			result = self.direct(data)

		if self.test:

			test: Data | None = None
			if self.inverted:
				test = self.direct(result)
			else:
				test = self.inverse(result)

			if data != test:
				raise ValueError(f'Transform {self} not invertible for data {data}')

		return result

	def __invert__(self) -> typing.Self:
		return dataclasses.replace(self, inverted = not self.inverted)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transforms:

	Transform = Transform

	common: typing.Sequence[Transform]
	equal:  Transform

	@pydantic.validate_arguments
	def __call__(self, data: Data) -> Data:
		return functools.reduce(
			lambda result, t: t(result),
			self.common,
			data
		)

	@pydantic.validate_arguments
	def __invert__(self) -> typing.Self:
		return Transforms(
			common = [
				~t
				for t in reversed(self.common)
			],
			equal  = self.equal
		)