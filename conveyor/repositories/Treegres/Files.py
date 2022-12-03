import pathlib
import pydantic
import dataclasses
from typing import Callable
from __future__ import annotations

from ...core import Digest, Data



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Files:

	root: pathlib.Path
	suffix: str

	transform: Callable[[Data], Data] = dataclasses.field(default=lambda d: Data(value=d.value + b' '))

	@pydantic.validate_arguments
	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, digest.path).with_suffix(self.suffix)

	@pydantic.validate_arguments
	def append(self, data: Data) -> None:

		path = self.path(data.digest)

		try:
			with path.open('xb') as f:
				f.write(data.value)

		except FileExistsError:
			if data != Data(value=path.read_bytes()):
				return self.append(
					self.transform(data)
				)

	@pydantic.validate_arguments
	def __getitem__(self, digest: Digest) -> Data:
		return Data(
			value=self.path(digest).read_bytes(),
			test=digest
		)

	@pydantic.validate_arguments
	def __delitem__(self, digest: Digest) -> None:
		self.path(digest).unlink(missing_ok=True)