import zlib
import typing
import pytest
import pathlib
import pydantic
import datetime
import sqlalchemy

from conveyor.core import Worker, Mask
from conveyor.repositories import Files, Rows
from conveyor.core import Item, Query, Repository



@pytest.fixture
def item() -> Item:

	data = Item.Data(value=b'v')

	return Item(
		type     = Item.Type('type'),
		status   = Item.Status('status'),
		data     = data,
		metadata = Item.Metadata({Item.Metadata.Key('key'): 'value'}),
		chain    = Item.Chain(ref=data),
		created  = Item.Created(value=datetime.datetime.utcnow()),
		reserver = Item.Reserver(exists=False)
	)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class RemoveLast(Files.Core.Transforms.Safe[bytes, bytes]):

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return i[:-1]

	def __invert__(self) -> 'AddSpace':
		return AddSpace()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class AddSpace(Files.Core.Transforms.Safe[bytes, bytes]):

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return i + b' '

	def __invert__(self) -> RemoveLast:
		return RemoveLast()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Compress(Files.Core.Transforms.Safe[bytes, bytes]):

	level: int

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return zlib.compress(i, level = self.level)

	def __invert__(self) -> 'Decompress':
		return Decompress(inverted_level = self.level)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Decompress(Files.Core.Transforms.Safe[bytes, bytes]):

	inverted_level: int

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return zlib.decompress(i)

	def __invert__(self) -> Compress:
		return Compress(level = self.inverted_level)


@pytest.fixture
def files() -> Files.Core:
	result = Files.Core(
		root     = pathlib.Path(__file__).parent / 'files',
		suffix   = '.txt',
		prepare  = Compress(level = 9),
		sidestep = AddSpace(),
		pathify  = Files.Core.Pathify(granulation = lambda n: 1024 if n > 1 else 1)
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


@pytest.fixture
def row() -> Rows.Core.Item:

	data = Item.Data(value=b'v')

	return Rows.Core.Item(
		type     = Item.Type('type'),
		status   = Item.Status('status'),
		digest   = data.digest,
		metadata = Item.Metadata({
			Item.Metadata.Key('key'): 'value'
		}),
		chain    = Item.Chain(ref=data).value,
		created  = Item.Created(datetime.datetime.utcnow()),
		reserver = Item.Reserver(exists=False)
	)


@pytest.fixture
def query_all(row: Rows.Core.Item) -> Query:
	return Query(
		mask = Query.Mask(
			type = row.type
		),
		limit = None
	)


@pytest.fixture
@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def repository(files: Files.Core, rows: Rows.Core) -> Repository:
	result = Repository([Rows(rows), Files(files)])
	result.clear()
	return result


@pytest.fixture
@pydantic.validate_arguments
def receiver(item: Item) -> Worker.Receiver:
	return Worker.Receiver(
		masks = (
			lambda _: Mask(
				type = item.type
			),
		),
		limit = None
	)