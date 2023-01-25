import pydantic
import sqlalchemy
import sqlalchemy.exc

from .....core import Transforms, Item

from .. import Cache
from ..Connect import Connect
from ..DbTableName import DbTableName

from .Columns import columns


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class EnumsTransform:

	connect:    Connect
	enum_table: str
	cache_id:   str

	@property
	def cache(self) -> Cache.Enums.Cache:
		return Cache.cache[self.cache_id]

	def load(self) -> None:
		self.cache.load(self.enum_table, self.connect)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Int(EnumsTransform, Transforms.Trusted[Item.Metadata.Enumerable, int]):

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
				self.load()
				return self.cache[self.enum_table].value[i]
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
			cache_id   = self.cache_id
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class String(EnumsTransform, Transforms.Trusted[int, Item.Metadata.Enumerable]):

	@pydantic.validate_arguments
	def transform(self, i: int) -> Item.Metadata.Enumerable:

		try:
			return self.cache[self.enum_table].description[i]
		except KeyError:
			pass

		try:
			self.load()
			return self.cache[self.enum_table].description[i]
		except Exception as e:
			raise ValueError(f'No description found for enum value `{i}` in table `{self.enum_table}`') from e

	def __invert__(self) -> Int:
		return Int(
			connect    = self.connect,
			enum_table = self.enum_table,
			cache_id   = self.cache_id
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Enum:

	type:           Item.Type
	type_transform: Transforms.Safe[Item.Type, str]


	field:          Item.Metadata.Key
	enum_transform: Transforms.Safe[Item.Metadata.Key,  str]

	connect:        Connect
	cache_id:       str

	@property
	def db_type(self) -> str:
		return self.type_transform(self.type)

	@property
	def db_field(self) -> str:
		return self.enum_transform(self.field)

	@property
	def table(self) -> sqlalchemy.Table:
		return sqlalchemy.Table(
			DbTableName(f'_conveyor_enum_{self.type.value}')(Item.Type(self.field.value)),
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
			cache_id   = self.cache_id
		)

	@property
	def String(self) -> String:
		return String(
			connect    = self.connect,
			enum_table = self.table.name,
			cache_id   = self.cache_id
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Enums:

	connect:        Connect
	cache_id:       str

	type_transform: Transforms.Safe[Item.Type, str]
	enum_transform: Transforms.Safe[Item.Metadata.Key,  str]

	def __getitem__(self, table_and_field: tuple[Item.Type, Item.Metadata.Key]):
		return Enum(
			connect        = self.connect,
			cache_id       = self.cache_id,
			type           = table_and_field[0],
			type_transform = self.type_transform,
			field          = table_and_field[1],
			enum_transform = self.enum_transform
		)