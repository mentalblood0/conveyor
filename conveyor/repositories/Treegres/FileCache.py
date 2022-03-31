from functools import lru_cache
from dataclasses import dataclass

from . import File



@dataclass
class FileCache:

	size: int=1024

	def __post_init__(self):
		self.File = lru_cache(maxsize=self.size)(File)

	def __call__(self, path: str):
		return self.File(path)