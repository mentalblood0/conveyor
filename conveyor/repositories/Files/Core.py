import typing
import pathlib
import pydantic
import contextlib
import dataclasses

from .Transaction import Transaction
from ...core.Item import Digest, Data



@pydantic.validate_arguments
def default_transform(d: Data) -> Data:
	return Data(value=d.value + b' ')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Core:

	root: pathlib.Path
	suffix: pydantic.StrictStr

	transform: typing.Callable[[Data], Data] = dataclasses.field(default=default_transform)
	transaction_: Transaction | None = None

	@pydantic.validate_arguments
	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, digest.path).with_suffix(self.suffix)

	@pydantic.validate_arguments
	def append(self, data: Data) -> None:
		with self.transaction() as t:
			if t.transaction_ is not None:
				t.transaction_.add([Transaction.Append(self.path(data.digest), data=data.value)])
			else:
				raise ValueError

	@pydantic.validate_arguments
	def __getitem__(self, digest: Digest) -> Data:
		try:
			return Data(
				value=self.path(digest).read_bytes(),
				test=digest
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