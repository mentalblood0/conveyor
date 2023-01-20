import pydantic

from ....core import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class TableEnumCache:
	value:       dict[Item.Metadata.Enumerable, int]
	description: dict[int, Item.Metadata.Enumerable]


EnumsCache = dict[str, TableEnumCache]


class Cache(dict[str, EnumsCache]):

	def __getitem__(self, __key: str) -> EnumsCache:
		if not __key in self:
			self[__key] = {}
		return super().__getitem__(__key)


cache = Cache()