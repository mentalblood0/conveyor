import typing
import pathlib
import pydantic
import dataclasses

from ...core import Digest, Data, Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class File:

	data_or_digest: Data | Digest

	@property
	def data(self):
		match self.data_or_digest:
			case Data():
				return self.data_or_digest
			case Digest():
				raise AttributeError
			case _ as unreachable:
				typing.assert_never(unreachable)

	@property
	def digest(self):
		match self.data_or_digest:
			case Data():
				return self.data_or_digest.digest
			case Digest():
				return self.data_or_digest
			case _ as unreachable:
				typing.assert_never(unreachable)

	@classmethod
	@pydantic.validate_arguments
	def from_item(cls, item: Item):
		return File(
			item.data
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Files:

	Item = File

	root: pathlib.Path
	suffix: pydantic.StrictStr

	transform: typing.Callable[[Data], Data] = dataclasses.field(default=lambda d: Data(value=d.value + b' '))

	@pydantic.validate_arguments
	def path(self, digest: Digest) -> pathlib.Path:
		return pathlib.Path(self.root, digest.path).with_suffix(self.suffix)

	@pydantic.validate_arguments
	def add(self, file: File) -> None:

		path = self.path(file.data.digest)
		path.parent.mkdir(parents=True, exist_ok=True)

		try:
			with path.open('xb') as f:
				f.write(file.data.value)

		except FileExistsError:
			if file.data != Data(value=path.read_bytes()):
				self.add(
					File(
						self.transform(file.data)
					)
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
	def __delitem__(self, file: File) -> None:

		p = self.path(file.digest)
		p.unlink(missing_ok=True)

		while len(p.parts) > 1:
			p = p.parent
			try:
				p.rmdir()
			except OSError:
				break

	@pydantic.validate_arguments
	def __contains__(self, file: File) -> bool:
		return self.path(file.digest).exists()