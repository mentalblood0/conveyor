import lzma
import base64
from blake3 import blake3
from dataclasses import dataclass



def getDigest(data: bytes) -> str:
	d = blake3(data, max_threads=blake3.AUTO).digest()
	return base64.b64encode(d).decode('ascii')


@dataclass
class File:

	path: str

	extension = '.xz'

	def set(self, content: bytes) -> None:

		with lzma.open(self.path, 'wb', filters=[
			{"id": lzma.FILTER_LZMA2, "preset": lzma.PRESET_EXTREME},
		]) as f:
			f.write(content)

		self.content = content.decode()
		self.correct_digest = getDigest(content)

	def get(self, digest: str) -> str:

		if not hasattr(self, 'content'):

			with lzma.open(self.path, 'rb') as f:
				file_bytes = f.read()

			self.content = file_bytes.decode()
			self.correct_digest = getDigest(file_bytes)

		if self.correct_digest != digest:
			raise Exception(f"Cannot get file content: digest invalid: '{digest}' != '{self.correct_digest}'")

		return self.content