import typing
import pydantic
import functools

from ...core.Item import Data



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Transform:

	inverted: bool = False

	def direct(self, data: Data) -> Data:
		raise NotImplementedError

	def inverse(self, data: Data) -> Data:
		raise NotImplementedError

	@pydantic.validate_arguments
	def __call__(self, data: Data) -> Data:
		if self.inverted:
			return self.inverse(data)
		else:
			return self.direct(data)

	def __invert__(self) -> typing.Self:
		return self.__class__(inverted = not self.inverted)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Invertible:

	transform: Transform
	data:      Data

	@pydantic.validator('data')
	def transform_invertible_for_data(cls, data: Data, values: dict[str, Transform | Data]) -> Data:
		match transform := values['transform']:
			case Transform():
				if (~transform)(transform(data)) != data:
					raise ValueError(f'Transform {transform} not invertible for data {data}')
			case _:
				raise ValueError

		return data

	def __call__(self) -> Data:
		return self.transform(self.data)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transforms:

	Transform = Transform

	common: list[Transform]
	equal:  Transform

	@pydantic.validate_arguments
	def __call__(self, data: Data) -> Data:
		return functools.reduce(
			lambda result, t: Invertible(
				transform = t,
				data      = result
			)(),
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