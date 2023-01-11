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


@pydantic.validate_arguments
def withSpace(i: bytes) -> bytes:
	return i + b' '

@pydantic.validate_arguments
def withoutLast(i: bytes) -> bytes:
	return i[:-1]


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class RemoveLast(Files.Core.Transforms.Transform[bytes, bytes]):

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return i[:-1]

	def __invert__(self: 'Files.Core.Transforms.Transform[bytes, bytes]') -> 'Files.Core.Transforms.Transform[bytes, bytes]':
		return AddSpace()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class AddSpace(Files.Core.Transforms.Transform[bytes, bytes]):

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return i + b' '

	def __invert__(self: 'Files.Core.Transforms.Transform[bytes, bytes]') -> 'Files.Core.Transforms.Transform[bytes, bytes]':
		return RemoveLast()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Compress(Files.Core.Transforms.Transform[bytes, bytes]):

	level: int

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return zlib.compress(i, level = self.level)

	def __invert__(self: Files.Core.Transforms.Transform[bytes, bytes]) -> Files.Core.Transforms.Transform[bytes, bytes]:
		return Decompress(inverted_level = 9)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Decompress(Files.Core.Transforms.Transform[bytes, bytes]):

	inverted_level: int = 9

	@pydantic.validate_arguments
	def transform(self, i: bytes) -> bytes:
		return zlib.decompress(i)

	def __invert__(self: Files.Core.Transforms.Transform[bytes, bytes]) -> Files.Core.Transforms.Transform[bytes, bytes]:
		return Compress(level = 9)


@pytest.fixture
def files() -> Files.Core:
	result = Files.Core(
		root        = pathlib.Path(__file__).parent / 'files',
		suffix      = '.txt',
		granulation = 4,
		transform   = Files.Core.Transforms((Compress(level = 9), Compress(level = 9))),
		equal       = AddSpace()
	)
	result.clear()
	return result


@pytest.fixture
def db() -> sqlalchemy.engine.Engine:
	return sqlalchemy.create_engine("sqlite://", echo=True)


@pytest.fixture
def rows(db: sqlalchemy.Engine) -> Rows.Core:
	return Rows.Core(db)