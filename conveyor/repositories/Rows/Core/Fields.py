import typing
import pydantic
import datetime
import sqlalchemy

from ....core import Item, Transforms

from .Enums import Enums



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


Column = sqlalchemy.Column[int] | sqlalchemy.Column[float] | sqlalchemy.Column[str] | sqlalchemy.Column[datetime.datetime]


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Field:

	name      : BaseField | Item.Metadata.Key
	value     : Item.Metadata.Value

	table     : Item.Type
	transform : Transforms.Safe[Item.Type, str]

	enums     : Enums.Enums

	@property
	def db_name(self) -> BaseField | str:
		return self.column.name

	@property
	def db_table(self) -> str:
		return self.transform(self.table)

	@property
	def column(self) -> Column:
		match self.name:
			case 'status':
				return         self.enums[(self.table, Item.Metadata.Key(self.name))].column
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
					case Item.Metadata.Enumerable():
						return self.enums[(self.table, self.name)].column
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
				match self.value:
					case Item.Metadata.Enumerable():
						return self.enums[(self.table, self.name)].index(table)
					case _:
						return sqlalchemy.Index(f'index__{self.name.value}', self.name.value, _table = table)
			case 'status':
				return self.enums[(self.table, Item.Metadata.Key(self.name))].index(table)
			case _:
				return sqlalchemy.Index(f'index__{self.name}', self.name, _table = table)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Fields:

	metadata  : Item.Metadata
	db        : sqlalchemy.Engine

	table     : Item.Type
	transform : Transforms.Safe[Item.Type, str]

	enums     : Enums.Enums

	@property
	def fields(self) -> typing.Iterable[Field]:
		for n in base_fields:
			yield Field(
				name      = n,
				value     = None,
				table     = self.table,
				enums     = self.enums,
				transform = self.transform
			)
		for k, v in self.metadata.value.items():
			yield Field(
				name      = k,
				value     = v,
				table     = self.table,
				enums     = self.enums,
				transform = self.transform
			)

	@property
	def columns(self) -> typing.Iterable[Column]:
		for f in self.fields:
			yield f.column