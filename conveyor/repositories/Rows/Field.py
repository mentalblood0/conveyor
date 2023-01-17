import typing
import pydantic
import datetime
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


@pydantic.validate_arguments
def fields(metadata: Item.Metadata) -> typing.Iterable[Field]:
	for n in base_fields:
		yield Field(name_ = n, value = None)
	for k, v in metadata.value.items():
		yield Field(name_ = k, value = v)


@pydantic.validate_arguments
def columns(metadata: Item.Metadata) -> typing.Iterable[sqlalchemy.Column[typing.Any]]:
	for f in fields(metadata):
		yield f.column