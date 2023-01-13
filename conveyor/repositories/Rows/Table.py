import typing
import datetime
import pydantic
import sqlalchemy

from ...core import Item



BaseField = (
	typing.Literal['status'] |
	typing.Literal['digest'] |
	typing.Literal['chain'] |
	typing.Literal['created'] |
	typing.Literal['reserver']
)


base_fields: tuple[
	typing.Literal['status'],
	typing.Literal['digest'],
	typing.Literal['chain'],
	typing.Literal['created'],
	typing.Literal['reserver'],
] = (
	'status',
	'digest',
	'chain',
	'created',
	'reserver'
)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Field:

	name: BaseField | Item.Metadata.Key
	value: Item.Metadata.Value

	@property
	def column(self) -> sqlalchemy.Column[typing.Any]:
		match self.name:
			case 'status':
				return         sqlalchemy.Column(self.name,       sqlalchemy.String(127), nullable = False)
			case 'digest':
				return         sqlalchemy.Column(self.name,       sqlalchemy.String(127), nullable = False)
			case 'chain':
				return         sqlalchemy.Column(self.name,       sqlalchemy.String(127), nullable = False)
			case 'created':
				return         sqlalchemy.Column(self.name,       sqlalchemy.DateTime(timezone=False), nullable = False)
			case 'reserver':
				return         sqlalchemy.Column(self.name,       sqlalchemy.String(31),  nullable = True)
			case Item.Metadata.Key():
				match self.value:
					case str():
						return sqlalchemy.Column(self.name.value, sqlalchemy.String(255), nullable = True)
					case int():
						return sqlalchemy.Column(self.name.value, sqlalchemy.Integer(),   nullable = True)
					case float():
						return sqlalchemy.Column(self.name.value, sqlalchemy.Float(),     nullable = True)
					case datetime.datetime() | type(datetime.datetime()):
						return sqlalchemy.Column(self.name.value, sqlalchemy.DateTime(timezone=False), nullable = True)
					case None:
						raise ValueError(f'Can not guess column type corresponding to value with type `{type(self.value)}`')

	@pydantic.validate_arguments(config = {'arbitrary_types_allowed': True})
	def index(self, table: sqlalchemy.Table) -> sqlalchemy.Index:
		match self.name:
			case Item.Metadata.Key():
				return sqlalchemy.Index(f'index__{self.name.value}', self.name.value, _table = table)
			case _:
				return sqlalchemy.Index(f'index__{self.name}', self.name, _table = table)



tables = sqlalchemy.MetaData()


@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def Table(
	connection: sqlalchemy.Connection,
	name: Item.Type,
	metadata: Item.Metadata | None = None
) -> sqlalchemy.Table:

		name = Item.Type(f'conveyor_{name.value.lower()}')

		if metadata is None:

			with connection.begin_nested() as c:

				if name.value not in sqlalchemy.inspect(connection).get_table_names():
					raise KeyError(f'Table {name.value} not exists')

				result = sqlalchemy.Table(
					name.value,
					tables,
					autoload_with=connection
				)

				c.rollback()

			return result

		else:

			with connection.begin_nested() as _:

				fields = [
					Field(name = n, value = None)
					for n in base_fields
				] + [
					Field(name = k, value = v)
					for k, v in metadata.value.items()
				]

				if name.value not in sqlalchemy.inspect(connection).get_table_names():

					result = sqlalchemy.Table(
						name.value,
						sqlalchemy.MetaData(),
						*(f.column for f in fields)
					)
					result.create(bind = connection)

					for f in fields:
						i = f.index(result)
						if i not in result.indexes:
							i.create(bind = connection, checkfirst = True)

					return result

				else:

					return sqlalchemy.Table(
						name.value,
						tables,
						*(f.column for f in fields),
						extend_existing = True
					)
