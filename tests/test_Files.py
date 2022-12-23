import pytest
import pathlib
import pydantic
import dataclasses

from conveyor.core.Item import Data
from conveyor.repositories.Files import Files_



@pytest.fixture
def files() -> Files_:
	return Files_(root=pathlib.Path('tests/files'), suffix='.txt')


@pytest.fixture
def data() -> Data:
	return Data(value=b'')


@pydantic.validate_arguments
def test_immutable(files: Files_):
	with pytest.raises(dataclasses.FrozenInstanceError):
		files.value = b'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del files.value
	with pytest.raises(dataclasses.FrozenInstanceError):
		files.x = b'x'


@pydantic.validate_arguments
def test_path(files: Files_, data: Data):

	p = files._path(data.digest)

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
def test_append_get_delete(files: Files_, data: Data):

	files.add(data)
	assert files[data.digest] == data

	del files[data.digest]
	with pytest.raises(KeyError):
		files[data.digest]


@pydantic.validate_arguments
def test_delete_nonexistent(files: Files_, data: Data):
	del files[data.digest]