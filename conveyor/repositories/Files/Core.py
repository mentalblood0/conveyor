import typing
import pathlib
import pydantic
import dataclasses

from ...core.Item import Digest, Data



@pydantic.validate_arguments
def default_transform(d: Data) -> Data:
	return Data(value=d.value + b' ')


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Core:

	root: pathlib.Path
	suffix: pydantic.StrictStr

	transform: typing.Callable[[Data], Data] = dataclasses.field(default=default_transform)

	@pydantic.validate_arguments
	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, digest.path).with_suffix(self.suffix)

	@pydantic.validate_arguments
	def append(self, data: Data) -> None:
		if data.digest in self:
			if data != self[data.digest]:
				self.append(self.transform(data))
		else:
			path = self.path(data.digest)
			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_bytes(data.value)

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

		while p != self.root:
			p = p.parent
			try:
				p.rmdir()
			except OSError:
				break

	@pydantic.validate_arguments
	def __contains__(self, digest: Digest) -> bool:
		return self.path(digest).exists()