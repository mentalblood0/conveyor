import typing
import pathlib
import pydantic
import functools
import contextlib
import collections
import dataclasses

from .Transaction import Transaction
from ...core.Item import Digest, Data



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
		return self.__class__(inverted = True)


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


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class DefaultEqualTransform(Transform):

	@pydantic.validate_arguments
	def direct(self, data: Data) -> Data:
		return Data(value = data.value + b' ')

	@pydantic.validate_arguments
	def inverse(self, data: Data) -> Data:
		return Data(value = data.value[:-1])


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transforms:

	Transform = Transform

	common: typing.Iterable[Transform]
	equal:  Transform = DefaultEqualTransform()

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
			common = reversed(collections.deque(
				~t
				for t in self.common
			)),
			equal  = self.equal
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Core:

	root: pathlib.Path
	suffix: pydantic.StrictStr

	transforms: Transforms = Transforms(common = ())
	transaction_: Transaction | None = None

	@pydantic.validate_arguments
	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, digest.path).with_suffix(self.suffix)

	@pydantic.validate_arguments
	def append(self, data: Data) -> None:
		with self.transaction() as t:
			if t.transaction_ is not None:
				t.transaction_.add([
					Transaction.Append(
						path = self.path(data.digest),
						data = self.transforms(data).value
					)
				])
			else:
				raise ValueError

	@pydantic.validate_arguments
	def __getitem__(self, digest: Digest) -> Data:
		try:
			return dataclasses.replace(
				(~self.transforms)(
					Data(
						value = self.path(digest).read_bytes()
					)
				),
				test = digest
			)
		except:
			raise KeyError(f'{self.root} {digest.string}')

	@pydantic.validate_arguments
	def __delitem__(self, digest: Digest) -> None:
		with self.transaction() as t:
			if t.transaction_ is not None:
				t.transaction_.add([Transaction.Delete(self.path(digest))])
			else:
				raise ValueError

	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:

		if self.transaction_ is None:
			t = dataclasses.replace(
				self,
				transaction_ = Transaction()
			)
		else:
			t = self

		if t.transaction_ is None:
			raise ValueError

		try:
			yield t
		except:
			t.transaction_.rollback()
			raise

		if self.transaction_ is None:
			t.transaction_.commit()

	@pydantic.validate_arguments
	def __contains__(self, digest: Digest) -> bool:
		return self.path(digest).exists()

	def __len__(self) -> pydantic.NonNegativeInt:

		result: pydantic.NonNegativeInt = 0

		for p in self.root.rglob(f'*{self.suffix}'):
			print(p.name)
			result += 1

		return result

	def clear(self) -> None:
		for p in self.root.rglob(f'*{self.suffix}'):
			p.unlink()