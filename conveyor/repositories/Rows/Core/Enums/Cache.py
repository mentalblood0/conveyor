import pydantic
import sqlalchemy

from .....core import Item

from ..Connect import Connect

from .Columns import columns



@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class TableCache:
	value       : dict[Item.Metadata.Enumerable, int]
	description : dict[int, Item.Metadata.Enumerable]


class Cache(dict[str, TableCache]):

	TableCache = TableCache

	@pydantic.validate_arguments
	def load(self, table: str, connect: Connect):
		with connect() as connection:
			for r in connection.execute(
				sqlalchemy.sql
				.select(columns)
				.select_from(sqlalchemy.text(table))
			):
				value, description = r.value, Item.Metadata.Enumerable(r.description)
				if table in self:
					self[table].description[value] = description
					self[table].value[description] = value
				else:
					self[table] = TableCache(
						value       = {description: value},
						description = {value: description}
					)
