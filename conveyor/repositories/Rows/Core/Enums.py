import pydantic
import sqlalchemy
import dataclasses
import sqlalchemy.exc

from ....core import Transforms, Item

from .Connect import Connect
from .DbTableName import DbTableName



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class DbEnumName(Transforms.Safe[Item.Key, str]):

	postfix: str

	@pydantic.validate_arguments
	def transform(self, i: Item.Key) -> str:
		return f'{i.value}_{self.postfix}'

	def __invert__(self) -> 'ItemKey':
		return ItemKey(self.postfix)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class ItemKey(Transforms.Safe[str, Item.Key]):

	postfix: str

	@pydantic.validate_arguments
	def transform(self, i: str) -> Item.Key:
		return Item.Key(i[:-len(self.postfix) - 1])

	def __invert__(self) -> DbEnumName:
		return DbEnumName(self.postfix)


columns = lambda: (
	sqlalchemy.Column('value',       sqlalchemy.Integer(),   nullable = False, primary_key = True, autoincrement = 'auto'),
	sqlalchemy.Column('description', sqlalchemy.String(127), nullable = False, unique      = True, index = True)
)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class TableEnumCache:
	value:       dict[Item.Metadata.Enumerable, int]
	description: dict[int, Item.Metadata.Enumerable]

Cache = dict[str, TableEnumCache]


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Int(Transforms.Trusted[Item.Metadata.Enumerable, int]):

	connect:    Connect
	enum_table: str
	cache:      Cache = dataclasses.field(default_factory = dict)

	@property
	def table(self):
		return sqlalchemy.Table(
			self.enum_table,
			sqlalchemy.MetaData(),
			*columns()
		)

	@pydantic.validate_arguments
	def transform(self, i: Item.Metadata.Enumerable) -> int:

		try:
			return self.cache[self.enum_table].value[i]
		except KeyError:
			pass

		while True:

			try:

				with self.connect() as connection:

					result = connection.execute(
						sqlalchemy.sql
						.select(sqlalchemy.text('value'))
						.select_from(sqlalchemy.text(self.enum_table))
						.where(sqlalchemy.column('description') == i.value)
					).scalar_one()

					if self.enum_table in self.cache:
						self.cache[self.enum_table].description[result] = i
						self.cache[self.enum_table].value[i]            = result
					else:
						self.cache[self.enum_table] = TableEnumCache(
							value       = {i: result},
							description = {result: i}
						)

					return result

			except:
				pass

			try:
				with self.connect() as connection:
					connection.execute(
						self.table.insert().values(({
							'description': i.value
						},))
					)
			except:
				pass

			with self.connect() as connection:
				self.table.create(bind = connection)
				connection.execute(
					self.table.insert().values(({
						'description': i.value
					},))
				)

	def __invert__(self) -> 'String':
		return String(
			connect    = self.connect,
			enum_table = self.enum_table,
			cache      = self.cache
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class String(Transforms.Trusted[int, Item.Metadata.Enumerable]):

	connect:    Connect
	enum_table: str
	cache:      Cache = dataclasses.field(default_factory = dict)

	@pydantic.validate_arguments
	def transform(self, i: int) -> Item.Metadata.Enumerable:

		try:
			return self.cache[self.enum_table].description[i]
		except KeyError:
			pass

		try:

			with self.connect() as connection:

				result = Item.Metadata.Enumerable(
					connection.execute(
						sqlalchemy.sql
						.select(sqlalchemy.text('description'))
						.select_from(sqlalchemy.text(self.enum_table))
						.where(sqlalchemy.column('value') == i)
						.limit(1)
					).scalar_one()
				)

				if self.enum_table in self.cache:
					self.cache[self.enum_table].value[result] = i
					self.cache[self.enum_table].description[i] = result
				else:
					self.cache[self.enum_table] = TableEnumCache(
						value       = {result: i},
						description = {i: result}
					)

				return result

		except:
			raise ValueError(f'No description found for enum value `{i}` in table `{self.enum_table}`') from e

	def __invert__(self) -> Int:
		return Int(
			connect    = self.connect,
			enum_table = self.enum_table,
			cache      = self.cache
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Enum:

	type:           Item.Type
	type_transform: Transforms.Safe[Item.Type, str]


	field:          Item.Key
	enum_transform: Transforms.Safe[Item.Key,  str]

	connect:        Connect
	cache:          Cache = dataclasses.field(default_factory = dict)

	@property
	def db_type(self) -> str:
		return self.type_transform(self.type)

	@property
	def db_field(self) -> str:
		return self.enum_transform(self.field)

	@property
	def table(self) -> sqlalchemy.Table:
		return sqlalchemy.Table(
			DbTableName(f'_conveyor_enum_{self.type.value}')(self.field),
			sqlalchemy.MetaData(),
			*columns()
		)

	@property
	def column(self) -> sqlalchemy.Column[int]:
		return sqlalchemy.Column(self.db_field, sqlalchemy.SmallInteger(), nullable = False)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def index(self, table: sqlalchemy.Table) -> sqlalchemy.Index[int]:
		return sqlalchemy.Index(f'index__{self.table.name}', self.db_field, _table = table)

	@pydantic.validate_arguments
	def eq(self, description: Item.Metadata.Enumerable) -> sqlalchemy.sql.expression.ColumnElement[bool]:
		return self.column == self.Int(description)

	@property
	def Int(self) -> Int:
		return Int(
			connect    = self.connect,
			enum_table = self.table.name,
			cache      = self.cache
		)

	@property
	def String(self) -> String:
		return String(
			connect    = self.connect,
			enum_table = self.table.name,
			cache      = self.cache
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Enums:

	connect:        Connect
	cache:          Cache = dataclasses.field(default_factory = dict)

	type_transform: Transforms.Safe[Item.Type, str]
	enum_transform: Transforms.Safe[Item.Key,  str]

	def __getitem__(self, table_and_field: tuple[Item.Type, Item.Key]):
		return Enum(
			connect        = self.connect,
			cache          = self.cache,
			type           = table_and_field[0],
			type_transform = self.type_transform,
			field          = table_and_field[1],
			enum_transform = self.enum_transform
		)