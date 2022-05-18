import lzma
import base64
import pydantic
from blake3 import blake3



@pydantic.validate_arguments
def getDigest(data: bytes) -> str:
	d = blake3(data, max_threads=blake3.AUTO).digest()
	return base64.b64encode(d).decode('ascii')


@pydantic.dataclasses.dataclass
class File:

	path: str
	encoding: str

	@pydantic.validate_arguments
	def set(self, content: str) -> None:

		content_bytes = content.encode(self.encoding)

		with lzma.open(self.path, 'wb', filters=[
			{"id": lzma.FILTER_LZMA2, "preset": lzma.PRESET_EXTREME},
		]) as f:
			f.write(content_bytes)

		self.content = content
		self.correct_digest = getDigest(content_bytes)

	@pydantic.validate_arguments
	def get(self, digest: str) -> str:

		if not hasattr(self, 'content'):

			with lzma.open(self.path, 'rb') as f:
				file_bytes = f.read()

			self.content = file_bytes.decode(self.encoding)
			self.correct_digest = getDigest(file_bytes)

		if self.correct_digest != digest:
			raise Exception(f"Cannot get file content: digest invalid: '{digest}' != '{self.correct_digest}'")

		return self.content