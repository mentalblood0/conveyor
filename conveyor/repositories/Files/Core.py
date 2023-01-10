import typing
import pathlib
import pydantic
import contextlib
import dataclasses

from .Transforms import Transforms
from .Transaction import Transaction
from ...core.Item import Digest, Data



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Core:

	Transforms = Transforms

	root: pathlib.Path
	suffix: pydantic.StrictStr

	transforms: Transforms[bytes]
	equal:      Transforms[bytes]

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
						path  = self.path(data.digest),
						data  = self.transforms(data.value),
						equal_path = lambda b: self.path(Data(value = b).digest),
						equal_data = self.equal
					)
				])
			else:
				raise ValueError

	@pydantic.validate_arguments
	def __getitem__(self, digest: Digest) -> Data:
		try:
			return Data(
				value = (~self.transforms)(
					self.path(digest).read_bytes()
				),
				test = digest
			)
		except FileNotFoundError:
			raise KeyError(f'{self.root} {digest.string}')
		except ValueError:
			raise

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
			if self.transaction_ is None:
				t.transaction_.commit()
		except:
			t.transaction_.rollback()
			raise

	@pydantic.validate_arguments
	def __contains__(self, digest: Digest) -> bool:
		return self.path(digest).exists()

	def __len__(self) -> pydantic.NonNegativeInt:

		result: pydantic.NonNegativeInt = 0

		for _ in self.root.rglob(f'*{self.suffix}'):
			result += 1

		return result

	def clear(self) -> None:

		for p in [*self.root.rglob(f'*{self.suffix}')]:

			p.unlink()

			d = p.parent
			while True:
				try:
					d.rmdir()
				except:
					break
				d = d.parent
