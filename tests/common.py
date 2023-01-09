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
class DefaultEqualTransform(Files.Core.Transforms.Transform):

	@pydantic.validate_arguments
	def direct(self, data: Item.Data) -> Item.Data:
		return Item.Data(value = data.value + b' ')

	@pydantic.validate_arguments
	def inverse(self, data: Item.Data) -> Item.Data:
		return Item.Data(value = data.value[:-1])


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Compress(Files.Core.Transforms.Transform):

	@pydantic.validate_arguments
	def direct(self, data: Item.Data) -> Item.Data:
		return Item.Data(value = zlib.compress(data.value, level = 9))

	@pydantic.validate_arguments
	def inverse(self, data: Item.Data) -> Item.Data:
		return Item.Data(value = zlib.decompress(data.value))


@pytest.fixture
def files() -> Files.Core:
	result = Files.Core(
		root       = pathlib.Path('tests/files'),
		suffix     = '.txt',
		transforms = Files.Core.Transforms(
			common = [Compress()],
			equal = DefaultEqualTransform()
		)
	)
	result.clear()
	return result


@pytest.fixture
def db() -> sqlalchemy.engine.Engine:
	return sqlalchemy.create_engine("sqlite://", echo=True)


@pytest.fixture
def rows(db: sqlalchemy.Engine) -> Rows:
	return Rows(Rows.Core(db))