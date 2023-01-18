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
		return Item.Key(i[:len(self.postfix) + 2])

	def __invert__(self) -> DbEnumName:
		return DbEnumName(self.postfix)


columns = lambda: (
	sqlalchemy.Column('value',       sqlalchemy.Integer(),   nullable = False, primary_key = True, autoincrement = 'auto'),
	sqlalchemy.Column('description', sqlalchemy.String(127), nullable = False)
)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Int(Transforms.Trusted[str, int]):

	connect:    Connect
	table_name: str
	field:      str

	@property
	def table(self):
		return sqlalchemy.Table(
			self.table_name,
			sqlalchemy.MetaData(),
			*columns()
		)

	@pydantic.validate_arguments
	def transform(self, i: str) -> int:

		if i is None:
			raise ValueError(f'`value` must be specified')

		while True:
			try:
				with self.connect() as connection:
					return connection.execute(
						sqlalchemy.sql
						.select(sqlalchemy.text('value'))
						.select_from(sqlalchemy.text(self.table_name))
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
			table_name = self.table_name,
			field      = self.field
		)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class String(Transforms.Trusted[int, str]):

	connect:    Connect
	table_name: str
	field:      str

	@pydantic.validate_arguments
	def transform(self, i: int) -> str:
		try:
			with self.connect() as connection:
				return connection.execute(
					sqlalchemy.sql
					.select(sqlalchemy.text('description'))
					.select_from(sqlalchemy.text(self.table_name))
					.where(sqlalchemy.column('value') == i)
					.limit(1)
				).scalar_one()
		except Exception as e:
			raise ValueError(f'No description found for enum value `{i}`') from e

	def __invert__(self) -> Int:
		return Int(
			connect    = self.connect,
			table_name = self.table_name,
			field      = self.field
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
			table_name = table,
			field      = self.name_.value
		)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def String(self, connect: Connect, table: str) -> String:
		return String(
			connect    = connect,
			table_name = table,
			field      = self.name_.value
		)