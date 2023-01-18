import typing
import pydantic
import sqlalchemy
import sqlalchemy.exc

from ....core import Item

from .DbTableName import DbTableName



columns = lambda: (
	sqlalchemy.Column('value',       sqlalchemy.Integer(), primary_key = True, nullable = False, autoincrement = 'auto'),
	sqlalchemy.Column('description', sqlalchemy.String(127),    nullable = False)
)


class Enum(sqlalchemy.types.TypeDecorator[str]):

	impl = sqlalchemy.types.Integer()

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __init__(self, db: sqlalchemy.Engine, table: str, field: str):
		self.db = db
		self.table_name = DbTableName('_conveyor_enum')(Item.Type(f'{table}_{field}'))

	@property
	def table(self):
		return sqlalchemy.Table(
			self.table_name,
			sqlalchemy.MetaData(),
			*columns()
		)

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def process_bind_param(self, value: str | None, dialect: sqlalchemy.Dialect = sqlalchemy.Dialect()) -> int:

		if value is None:
			raise ValueError(f'`value` must be specified')

		while True:
			try:
				with self.db.connect() as connection:
					return connection.execute(
						sqlalchemy.sql
						.select(sqlalchemy.text('value'))
						.select_from(sqlalchemy.text(self.table_name))
						.where(sqlalchemy.column('description') == value)
						.limit(1)
					).scalar_one()
			except:
				try:
					with self.db.connect() as connection:
						connection.execute(
							self.table.insert().values(({
								'description': value
							},))
						)
						connection.commit()
				except:
					with self.db.connect() as connection:
						self.table.create(bind = connection)
						connection.commit()

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def process_result_value(self, value: typing.Any | None, dialect: sqlalchemy.Dialect = sqlalchemy.Dialect()) -> str | None:

		print('__________________________________________________PROCESS RESULT VALUE')

		if type(value) != int:
			raise ValueError(f'Type of `value` must be `int`')

		try:
			with self.db.connect() as connection:
				return connection.execute(
					sqlalchemy.sql
					.select(sqlalchemy.text('description'))
					.select_from(sqlalchemy.text(self.table_name))
					.where(sqlalchemy.column('value') == value)
					.limit(1)
				).scalar_one()
		except Exception as e:
			raise ValueError(f'No description found for enum value `{value}`') from e