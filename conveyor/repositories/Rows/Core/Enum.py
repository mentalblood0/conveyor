import pydantic
import sqlalchemy
import sqlalchemy.exc

from ....core import Transforms, Item

from .Connect import Connect



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
	sqlalchemy.Column('description', sqlalchemy.String(127), nullable = False, index = True)
)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Int(Transforms.Trusted[str, int]):

	connect:    Connect
	enum_table: str

	@property
	def table(self):
		return sqlalchemy.Table(
			self.enum_table,
			sqlalchemy.MetaData(),
			*columns()
		)

	@pydantic.validate_arguments
	def transform(self, i: str) -> int:

		while True:
			try:
				with self.connect() as connection:
					return connection.execute(
						sqlalchemy.sql
						.select(sqlalchemy.text('value'))
						.select_from(sqlalchemy.text(self.enum_table))
						.where(sqlalchemy.column('description') == i)
						.limit(1)
					).scalar_one()
			except:
				try:
					with self.connect() as connection:
						connection.execute(
							self.table.insert().values(({
								'description': i
							},))
						)
				except:
					with self.connect() as connection:
						self.table.create(bind = connection)

	def __invert__(self) -> 'String':
		return String(
			connect    = self.connect,
			enum_table = self.enum_table
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class String(Transforms.Trusted[int, str]):

	connect:    Connect
	enum_table: str

	@pydantic.validate_arguments
	def transform(self, i: int) -> str:
		try:
			with self.connect() as connection:
				return connection.execute(
					sqlalchemy.sql
					.select(sqlalchemy.text('description'))
					.select_from(sqlalchemy.text(self.enum_table))
					.where(sqlalchemy.column('value') == i)
					.limit(1)
				).scalar_one()
		except Exception as e:
			raise ValueError(f'No description found for enum value `{i}` in table `{self.enum_table}`') from e

	def __invert__(self) -> Int:
		return Int(
			connect    = self.connect,
			enum_table = self.enum_table
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Enum:

	name_:     Item.Key
	transform: Transforms.Safe[Item.Key, str]

	@property
	def name(self) -> str:
		return self.transform(self.name_)

	@property
	def column(self) -> sqlalchemy.Column[int]:
		return sqlalchemy.Column(self.name, sqlalchemy.SmallInteger(), nullable = False)

	def index(self, table: sqlalchemy.Table) -> sqlalchemy.Index[int]:
		return sqlalchemy.Index(f'index__{self.name}', self.name, _table = table)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def Int(self, connect: Connect, table: str) -> Int:
		return Int(
			connect    = connect,
			enum_table = self.name
		)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def String(self, connect: Connect, table: str) -> String:
		return String(
			connect    = connect,
			enum_table = self.name
		)