import typing
import shutil
import pathlib
import pydantic
import contextlib
import dataclasses

from conveyor.core.Item import Digest, Data

from ....core import Transforms
from .Pathify import Pathify
from .Transaction import Transaction



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Core:

	Transforms = Transforms
	Pathify    = Pathify

	root         : pathlib.Path
	suffix       : str

	prepare      : Transforms.Transform[bytes, bytes]
	sidestep     : Transforms.Transform[bytes, bytes]
	pathify      : Transforms.Transform[Digest, pathlib.Path]

	transaction_ : Transaction | None                         = None

	@pydantic.validate_arguments
	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, self.pathify(digest)).with_suffix(self.suffix)

	@pydantic.validate_arguments
	def append(self, data: Data) -> None:
		with self.transaction() as t:
			if t.transaction_ is not None:
				t.transaction_.append(
					Transaction.Append(
						path       = self.path(data.digest),
						data       = data.value,
						transforms = self.prepare,
						equal_path = lambda b: self.path(Data(value = b).digest),
						equal_data = self.sidestep
					)
				)
			else:
				raise ValueError

	@pydantic.validate_arguments
	def __getitem__(self, digest: Digest) -> Data:
		try:
			return Data(
				value = (~self.prepare)(
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
				t.transaction_.append(Transaction.Delete(self.path(digest)))
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
			try:
				yield t
				if self.transaction_ is None:
					t.transaction_.commit()
			except:
				t.transaction_.rollback()
				raise
		except FileNotFoundError as e:
			raise KeyError from e

	@pydantic.validate_arguments
	def __contains__(self, digest: Digest) -> bool:
		return self.path(digest).exists()

	def __len__(self) -> pydantic.NonNegativeInt:

		result: pydantic.NonNegativeInt = 0

		for _ in self.root.rglob(f'*{self.suffix}'):
			result += 1

		return result

	def clear(self) -> None:
		shutil.rmtree(self.root, ignore_errors=True)