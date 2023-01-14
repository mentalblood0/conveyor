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

	name_:  BaseField | Item.Metadata.Key
	value: Item.Metadata.Value

	@property
	def name(self) -> BaseField | str:
		match self.name_:
			case Item.Metadata.Key():
				return self.name_.value
			case _:
				return self.name_

	@property
	def column(self) -> sqlalchemy.Column[typing.Any]:
		match self.name_:
			case 'status':
				return         sqlalchemy.Column(self.name_,       sqlalchemy.String(127), nullable = False)
			case 'digest':
				return         sqlalchemy.Column(self.name_,       sqlalchemy.String(127), nullable = False)
			case 'chain':
				return         sqlalchemy.Column(self.name_,       sqlalchemy.String(127), nullable = False)
			case 'created':
				return         sqlalchemy.Column(self.name_,       sqlalchemy.DateTime(timezone=False), nullable = False)
			case 'reserver':
				return         sqlalchemy.Column(self.name_,       sqlalchemy.String(31),  nullable = True)
			case Item.Metadata.Key():
				match self.value:
					case str():
						return sqlalchemy.Column(self.name_.value, sqlalchemy.String(255), nullable = True)
					case int():
						return sqlalchemy.Column(self.name_.value, sqlalchemy.Integer(),   nullable = True)
					case float():
						return sqlalchemy.Column(self.name_.value, sqlalchemy.Float(),     nullable = True)
					case datetime.datetime() | type(datetime.datetime()):
						return sqlalchemy.Column(self.name_.value, sqlalchemy.DateTime(timezone=False), nullable = True)
					case None:
						raise ValueError(f'Can not guess column type corresponding to value with type `{type(self.value)}`')

	@pydantic.validate_arguments(config = {'arbitrary_types_allowed': True})
	def index(self, table: sqlalchemy.Table) -> sqlalchemy.Index:
		match self.name_:
			case Item.Metadata.Key():
				return sqlalchemy.Index(f'index__{self.name_.value}', self.name_.value, _table = table)
			case _:
				return sqlalchemy.Index(f'index__{self.name_}', self.name_, _table = table)


tables = sqlalchemy.MetaData()


@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def Table(
	connection: sqlalchemy.Connection,
	name:       Item.Type,
	metadata:   Item.Metadata
) -> sqlalchemy.Table:

		name = Item.Type(f'conveyor_{name.value.lower()}')

		with connection.begin_nested() as _:

			fields = {
				Field(name_ = n, value = None)
				for n in base_fields
			} | {
				Field(name_ = k, value = v)
				for k, v in metadata.value.items()
			}

			if name.value not in sqlalchemy.inspect(connection).get_table_names():

				result = sqlalchemy.Table(
					name.value,
					sqlalchemy.MetaData(),
					*(f.column for f in fields)
				)
				result.create(bind = connection)

				for i in result.indexes - {f.index(result) for f in fields}:
					i.create(bind = connection)

			else:

				result = sqlalchemy.Table(
					name.value,
					sqlalchemy.MetaData(),
					*(f.column for f in fields)
				)

				current_columns = {
					c['name']
					for c in sqlalchemy.inspect(connection).get_columns(name.value)
				}

				for f in fields:
					if f.name not in current_columns:
						connection.execute(sqlalchemy.sql.text(f'ALTER TABLE {name.value} ADD {f.column.name} {f.column.type}'))
						if not (i := f.index(result)) in result.indexes:
							i.create(bind = connection)

			return result
