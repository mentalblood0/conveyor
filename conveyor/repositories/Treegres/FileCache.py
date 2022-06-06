import ring
import pydantic
from functools import lru_cache

from . import File



def getFile(path: str, encoding: str):
	return File(path, encoding)


class FileCache:

	@pydantic.validate_arguments
	def __init__(self, size: int):
		self.getFile = ring.lru(maxsize=size)(getFile)

	@pydantic.validate_arguments
	def __call__(self, path: str, encoding: str) -> File:
		return self.getFile(path, encoding)

	@pydantic.validate_arguments
	def delete(self, path: str, encoding: str) -> None:
		self.getFile.delete(path, encoding)