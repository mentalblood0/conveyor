import pytest
import pathlib
import dataclasses

from conveyor.core import Data
from conveyor.repositories.Filows import Files



@pytest.fixture
def valid_files():
	return Files(root=pathlib.Path('.'), suffix='.txt')


@pytest.fixture
def data():
	return Data(value=b'')


def test_immutable(valid_files):
	with pytest.raises(dataclasses.FrozenInstanceError):
		valid_files.value = b'x'
	with pytest.raises(dataclasses.FrozenInstanceError):
		del valid_files.value
	with pytest.raises(dataclasses.FrozenInstanceError):
		valid_files.x = b'x'


def test_path(valid_files, data):

	p = valid_files.path(data.digest)

	p.parent.mkdir(parents=True, exist_ok=True)
	p.touch(exist_ok=True)

	p.unlink()
	while len(p.parts) > 1:
		p = p.parent
		p.rmdir()


def test_append_get_delete(valid_files, data):

	valid_files.add(data)
	assert valid_files[data.digest] == data

	del valid_files[data.digest]
	with pytest.raises(KeyError):
		valid_files[data.digest]


def test_delete_nonexistent(valid_files, data):
	del valid_files[data.digest]