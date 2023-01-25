import pydantic
import sqlalchemy

from ....core import Item

from .Connect import Connect



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class TableEnumCache:
	value:       dict[Item.Metadata.Enumerable, int]
	description: dict[int, Item.Metadata.Enumerable]


class EnumsCache(dict[str, TableEnumCache]):
	@pydantic.validate_arguments
	def load(self, table: str, connect: Connect):
		with connect() as connection:
			for r in connection.execute(
				sqlalchemy.sql
				.select(sqlalchemy.text('value, description'))
				.select_from(sqlalchemy.text(table))
			):
				value, description = r.value, Item.Metadata.Enumerable(r.description)
				if table in self:
					self[table].description[value] = description
					self[table].value[description] = value
				else:
					self[table] = TableEnumCache(
						value       = {description: value},
						description = {value: description}
					)


class Cache(dict[str, EnumsCache]):

	def __getitem__(self, __key: str) -> EnumsCache:
		if not __key in self:
			self[__key] = EnumsCache()
		return super().__getitem__(__key)


cache = Cache()