import zlib
import math
import typing
import pytest
import pathlib
import pydantic
import datetime
import sqlalchemy

from conveyor.core import Item
from conveyor.repositories import Files, Rows



@pytest.fixture
def item() -> Item:

	data = Item.Data(value=b'')

	return Item(
		type=Item.Type('type'),
		status=Item.Status('status'),
		data=data,
		metadata=Item.Metadata({Item.Metadata.Key('key'): 'value'}),
		chain=Item.Chain(ref=data),
		created=Item.Created(value=datetime.datetime.utcnow()),
		reserver=Item.Reserver(exists=False)
	)


@pydantic.validate_arguments
def withSpace(i: bytes) -> bytes:
	return i + b' '

@pydantic.validate_arguments
def withoutLast(i: bytes) -> bytes:
	return i[:-1]


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class RemoveLast(Files.Core.Transform[bytes, bytes]):

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return i[:-1]

	def __invert__(self) -> 'AddSpace':
		return AddSpace()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class AddSpace(Files.Core.Transform[bytes, bytes]):

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return i + b' '

	def __invert__(self) -> RemoveLast:
		return RemoveLast()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Compress(Files.Core.Transform[bytes, bytes]):

	level: int

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return zlib.compress(i, level = self.level)

	def __invert__(self) -> 'Decompress':
		return Decompress(inverted_level = 9)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Decompress(Files.Core.Transform[bytes, bytes]):

	inverted_level: int = 9

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return zlib.decompress(i)

	def __invert__(self) -> Compress:
		return Compress(level = 9)


@pytest.fixture
def files() -> Files.Core:
	result = Files.Core(
		root     = pathlib.Path(__file__).parent / 'files',
		suffix   = '.txt',
		prepare  = Compress(level = 9),
		sidestep = AddSpace(),
		pathify  = Files.Core.Pathify(granulation = lambda n: math.floor(n / 1.5) + 1)
	)
	result.clear()
	return result


DbType = typing.Literal['postgres'] | typing.Literal['sqlite']


@pytest.fixture
def db_type() -> DbType:
	return 'sqlite'


@pytest.fixture
def db(db_type: DbType) -> sqlalchemy.engine.Engine:
	match db_type:
		case 'postgres':
			return sqlalchemy.create_engine('postgresql+psycopg2://postgres:5924@10.8.5.171:5480/postgres', echo=True)
		case 'sqlite':
			return sqlalchemy.create_engine('sqlite://', echo=True)


@pytest.fixture
def rows(db: sqlalchemy.Engine) -> Rows.Core:
	result = Rows.Core(db)
	result.clear()
	return result