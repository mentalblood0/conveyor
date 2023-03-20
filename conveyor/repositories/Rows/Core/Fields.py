import typing
import pydantic
import datetime
import sqlalchemy
import dataclasses

from ....core import Item, Transforms

from .Row import Row
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

	name      : Item.Key
	value     : Item.Value | Item.Data.Digest

	table     : Item.Type
	transform : Transforms.Safe[Item.Type, str]

	enums     : Enums.Enums

	@property
	def db_name(self) -> str:
		return self.column.name

	@property
	def db_table(self) -> str:
		return self.transform(self.table)

	@property
	def column(self) -> Column:
		match self.value:
			case Item.Metadata.Enumerable():
				return self.enums[(self.table, self.name)].column
			case Item.Data.Digest():
				return sqlalchemy.Column(self.name.value, sqlalchemy.String(127),              nullable = False)
			case Item.Chain():
				return sqlalchemy.Column(self.name.value, sqlalchemy.String(127),              nullable = False)
			case Item.Created():
				return sqlalchemy.Column(self.name.value, sqlalchemy.DateTime(timezone=False), nullable = False)
			case Item.Reserver():
				return sqlalchemy.Column(self.name.value, sqlalchemy.String(31),               nullable = True)
			case str():
				return sqlalchemy.Column(self.name.value, sqlalchemy.String(255),              nullable = True)
			case int():
				return sqlalchemy.Column(self.name.value, sqlalchemy.Integer(),                nullable = True)
			case float():
				return sqlalchemy.Column(self.name.value, sqlalchemy.Float(),                  nullable = True)
			case datetime.datetime():
				return sqlalchemy.Column(self.name.value, sqlalchemy.DateTime(timezone=False), nullable = True)
			case _:
				raise ValueError(f'Can not guess column type corresponding to value with type `{type(self.value)}`')

	@pydantic.validate_arguments(config = {'arbitrary_types_allowed': True})
	def index(self, table: sqlalchemy.Table) -> sqlalchemy.Index:
		match self.value:
			case Item.Metadata.Enumerable():
				return self.enums[(self.table, self.name)].index(table)
			case _:
				return sqlalchemy.Index(f'index__{self.name.value}', self.name.value, _table = table)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True, config={'arbitrary_types_allowed': True})
class Fields:

	row       : Row
	db        : sqlalchemy.Engine

	table     : Item.Type
	transform : Transforms.Safe[Item.Type, str]

	enums     : Enums.Enums

	ignore = {'type', 'data', 'metadata'}

	@property
	def fields(self) -> typing.Iterable[Field]:

		for k in {f.name for f in dataclasses.fields(self.row)} - self.ignore:
			yield Field(
				name      = Item.Key(k),
				value     = getattr(self.row, k),
				table     = self.table,
				enums     = self.enums,
				transform = self.transform
			)

		for k in self.row.metadata.value:
			yield Field(
				name      = Item.Key(k.value),
				value     = self.row.metadata.value[k],
				table     = self.table,
				enums     = self.enums,
				transform = self.transform
			)

	@property
	def columns(self) -> typing.Iterable[Column]:
		for f in self.fields:
			yield f.column