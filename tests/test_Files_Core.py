import pytest
import pathlib
import pydantic

from conveyor.core.Item import Data
from conveyor.repositories import Files



@pytest.fixture
def files() -> Files.Core:
	return Files.Core(root=pathlib.Path('tests/files'), suffix='.txt')


@pytest.fixture
def data() -> Data:
	return Data(value=b'')


@pydantic.validate_arguments
def test_path(files: Files.Core, data: Data):

	p = files.path(data.digest)

	p.parent.mkdir(parents=True, exist_ok=True)
	p.touch(exist_ok=True)

	p.unlink()
	while len(p.parts) > 1:
		p = p.parent
		try:
			p.rmdir()
		except:
			pass


@pydantic.validate_arguments
def test_append_get_delete(files: Files.Core, data: Data):

	files.append(data)
	assert files[data.digest] == data

	del files[data.digest]
	with pytest.raises(KeyError):
		files[data.digest]


@pydantic.validate_arguments
def test_delete_nonexistent(files: Files.Core, data: Data):
	del files[data.digest]