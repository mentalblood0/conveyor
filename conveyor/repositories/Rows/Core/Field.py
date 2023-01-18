import enum
import typing
import pydantic
import datetime
import sqlalchemy

from ....core import Item, Transforms

from .Enum import Enum



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


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Field:

	name_: BaseField | Item.Metadata.Key
	value: Item.Metadata.Value

	db:    sqlalchemy.Engine
	table: str
	enum:  Transforms.Safe[Item.Key, str]

	@property
	def name(self) -> BaseField | str:
		return self.column.name

	@property
	def column(self) -> sqlalchemy.Column[typing.Any]:
		match self.name_:
			case 'status':
				return         Enum(name_ = Item.Key(self.name_), transform = self.enum).column
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
					case enum.Enum():
						return Enum(name_ = self.name_, transform = self.enum).column
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
			case 'status':
				return Enum(name_ = Item.Key(self.name_), transform = self.enum).index(table)
			case _:
				return sqlalchemy.Index(f'index__{self.name_}', self.name_, _table = table)


@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def fields(metadata: Item.Metadata, db: sqlalchemy.Engine, table: str, enum_: Transforms.Safe[Item.Key, str]) -> typing.Iterable[Field]:

	for n in base_fields:
		yield Field(
			name_ = n,
			value = None,
			enum  = enum_,
			db    = db,
			table = table
		)
	for k, v in metadata.value.items():
		yield Field(
			name_ = k,
			value = v,
			enum  = enum_,
			db    = db,
			table = table
		)


@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def columns(metadata: Item.Metadata, db: sqlalchemy.Engine, table: str, enum_: Transforms.Safe[Item.Key, str]) -> typing.Iterable[sqlalchemy.Column[typing.Any]]:
	for f in fields(metadata, db, table, enum_):
		result = f.column
		print(f'COLUMN {result}')
		yield result