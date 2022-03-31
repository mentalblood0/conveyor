from functools import lru_cache

from . import File



class FileCache:

	def __init__(self, size: int=1024):
		self.File = lru_cache(maxsize=size)(File)

	def __call__(self, path: str):
		return self.File(path)