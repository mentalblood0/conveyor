from functools import lru_cache

from . import File



class FileCache:

	def __init__(self, size: int):
		self.File = lru_cache(maxsize=size)(File)

	def __call__(self, path: str, encoding: str):
		return self.File(path, encoding)