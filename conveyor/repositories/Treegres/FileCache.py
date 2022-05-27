import pydantic
from functools import lru_cache

from . import File



class FileCache:

	@pydantic.validate_arguments
	def __init__(self, size: int):
		self.File = lru_cache(maxsize=size)(File)

	@pydantic.validate_arguments
	def __call__(self, path: str, encoding: str) -> File:
		return self.File(path, encoding)