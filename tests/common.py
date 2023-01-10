import zlib
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


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class DefaultEqualTransform(Files.Core.Transforms.Transform[bytes]):

	@pydantic.validate_arguments
	def direct(self, o: bytes) -> bytes:
		return o + b' '

	@pydantic.validate_arguments
	def inverse(self, o: bytes) -> bytes:
		return o[:-1]


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Compress(Files.Core.Transforms.Transform[bytes]):

	level: int = 9

	@pydantic.validate_arguments
	def direct(self, o: bytes) -> bytes:
		return zlib.compress(o, level = self.level)

	@pydantic.validate_arguments
	def inverse(self, o: bytes) -> bytes:
		return zlib.decompress(o)


@pytest.fixture
def files() -> Files.Core:
	result = Files.Core(
		root        = pathlib.Path(__file__).parent / 'files',
		suffix      = '.txt',
		granulation = 4,
		transform   = Compress(level = 9),
		equal       = DefaultEqualTransform()
	)
	result.clear()
	return result


@pytest.fixture
def db() -> sqlalchemy.engine.Engine:
	return sqlalchemy.create_engine("sqlite://", echo=True)


@pytest.fixture
def rows(db: sqlalchemy.Engine) -> Rows.Core:
	return Rows.Core(db)