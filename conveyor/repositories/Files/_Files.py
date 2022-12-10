import typing
import pathlib
import pydantic
import dataclasses

from ...core import Digest, Data


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class _Files:

	root: pathlib.Path
	suffix: pydantic.StrictStr

	transform: typing.Callable[[Data], Data] = dataclasses.field(default=lambda d: Data(value=d.value + b' '))

	@pydantic.validate_arguments
	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, digest.path).with_suffix(self.suffix)

	@pydantic.validate_arguments
	def add(self, data: Data) -> None:

		path = self.path(data.digest)
		path.parent.mkdir(parents=True, exist_ok=True)

		try:
			with path.open('xb') as f:
				f.write(data.value)

		except FileExistsError:
			if data != Data(value=path.read_bytes()):
				self.add(
					self.transform(data)
				)

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

		p = self.path(digest)
		p.unlink(missing_ok=True)

		while len(p.parts) > 1:
			p = p.parent
			try:
				p.rmdir()
			except OSError:
				break

	@pydantic.validate_arguments
	def __contains__(self, digest: Digest) -> bool:
		return self.path(digest).exists()