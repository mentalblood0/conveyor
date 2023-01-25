from . import Enums



class Cache(dict[str, Enums.Cache]):
	def __getitem__(self, __key: str) -> Enums.Cache:
		if not __key in self:
			self[__key] = Enums.Cache()
		return super().__getitem__(__key)


cache = Cache()