import typing
import shutil
import pathlib
import contextlib
import dataclasses

from conveyor.core.Item import Digest, Data

from ....core import Transforms
from .Pathify import Pathify
from .Transaction import Transaction


@dataclasses.dataclass(frozen = True, kw_only = True)
class Core:

	Transforms = Transforms
	Pathify    = Pathify

	root         : pathlib.Path
	suffix       : str

	prepare      : Transforms.Transform[bytes, bytes]
	sidestep     : Transforms.Transform[bytes, bytes]
	pathify      : Transforms.Transform[Digest, pathlib.Path]

	transaction_ : Transaction | None                         = None

	empty        : Digest = Data(value = b'').digest

	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, self.pathify(digest)).with_suffix(self.suffix)

	def append(self, data: Data) -> None:

		if not data.value:
			return

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

	def __getitem__(self, digest: Digest) -> Data:

		if digest == self.empty:
			return Data(value = b'')

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

	def __contains__(self, digest: Digest) -> bool:
		return self.path(digest).exists()

	def __len__(self) -> int:

		result: int = 0

		for _ in self.root.rglob(f'*{self.suffix}'):
			result += 1

		return result

	def clear(self) -> None:
		shutil.rmtree(self.root, ignore_errors=True)