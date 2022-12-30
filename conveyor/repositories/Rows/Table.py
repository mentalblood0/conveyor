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


@pydantic.validate_arguments
def Column(name: BaseField | Item.Metadata.Key, value: Item.Metadata.Value):
	match name:
		case 'status':
			return sqlalchemy.Column(name, sqlalchemy.String(63), primary_key=True, nullable=False)
		case 'digest':
			return sqlalchemy.Column(name, sqlalchemy.String(127), primary_key=True, nullable=False)
		case 'chain':
			return sqlalchemy.Column(name, sqlalchemy.String(127), primary_key=True, nullable=False)
		case 'created':
			return sqlalchemy.Column(name, sqlalchemy.DateTime(timezone=False), primary_key=True, nullable=False)
		case 'reserver':
			return sqlalchemy.Column(name, sqlalchemy.String(31), primary_key=True, nullable=True)
		case Item.Metadata.Key():
			match value:
				case str():
					return sqlalchemy.Column(name.value, sqlalchemy.String(255), primary_key=True)
				case int():
					return sqlalchemy.Column(name.value, sqlalchemy.Integer(), primary_key=True)
				case float():
					return sqlalchemy.Column(name.value, sqlalchemy.Float(), primary_key=True)
				case datetime.datetime() | type(datetime.datetime()):
					return sqlalchemy.Column(name.value, sqlalchemy.DateTime(timezone=False), primary_key=True)
				case None:
					raise ValueError(f'Can not guess column type corresponding to value with type `{type(value)}`')


tables = sqlalchemy.MetaData()


@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def Table(
	db: sqlalchemy.engine.Engine,
	name: Item.Type,
	metadata: Item.Metadata | None = None
) -> sqlalchemy.Table:

		name = Item.Type(name.value.lower())

		if metadata is None:

			if name.value not in sqlalchemy.inspect(db).get_table_names():
				raise KeyError(f'Table {name.value} not exists')

			return sqlalchemy.Table(
				name.value,
				tables,
				autoload_with=db
			)

		else:

			result = sqlalchemy.Table(
				name.value,
				tables,
				*(
					Column(name, None)
					for name in base_fields
				),
				*(
					Column(k, v)
					for k, v in metadata.value.items()
				),
				extend_existing=True
			)

			if name.value not in sqlalchemy.inspect(db).get_table_names():
				result.create(bind=db)

			return result
