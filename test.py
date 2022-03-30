from functools import lru_cache



class C:

	def __new__(c, path, content=None):
		return super(C, c).__new__(c, path, content)

	def __init__(self, path, content=None):
		super().__init__(path, content)
		self.content = content


C.__new__ = lru_cache()(C.__new__)
C('/1/2/3', 'lalala')

print(C.__new__.cache_info().hits)
print(C('/1/2/3').content)
print(C.__new__.cache_info().hits)