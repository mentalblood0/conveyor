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

	@property
	def correct_digest(self):

		if not hasattr(self, '_correct_digest'):
			self.get()

		return self._correct_digest

	@pydantic.validate_arguments
	def set(self, content: str) -> None:

		content_bytes = content.encode(self.encoding)

		with open(self.path, 'wb') as f:
			f.write(content_bytes)

		self.content = content
		self._correct_digest = getDigest(content_bytes)

	@pydantic.validate_arguments
	def get(self, digest: str=None) -> str:

		if not hasattr(self, 'content'):

			with open(self.path, 'rb') as f:
				file_bytes = f.read()

			self.content = file_bytes.decode(self.encoding)
			self._correct_digest = getDigest(file_bytes)

		if (digest) and (self._correct_digest != digest):
			raise Exception(f"Cannot get file content: digest invalid: '{digest}' != '{self._correct_digest}'")

		return self.content