import pytest

from conveyor.core.Item import Data
from conveyor.repositories import Files

from ..common import *



@pytest.fixture
def data() -> Data:
	return Data(value=b'v')


@pytest.fixture
def empty() -> Data:
	return Data(value=b'')


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


def test_append_one(files: Files.Core, data: Data):
	files.append(data)
	assert files[data.digest] == data


def test_append_empty(files: Files.Core, empty: Data):
	assert files[empty.digest]
	files.append(empty)
	assert files[empty.digest] == empty


def test_append_many_same(files: Files.Core, data: Data):
	for _ in range(3):
		files.append(data)
		assert files[data.digest] == data


def test_append_many(files: Files.Core, data: Data):
	for i in range(3):
		d = Data(value = data.value + str(i).encode())
		files.append(d)
		assert files[d.digest] == d


def test_append_get_delete(files: Files.Core, data: Data):

	files.append(data)
	assert files[data.digest] == data

	del files[data.digest]
	with pytest.raises(KeyError):
		files[data.digest]


def test_delete_nonexistent(files: Files.Core, data: Data):
	with pytest.raises(KeyError):
		del files[data.digest]


def test_transaction_append_one(files: Files.Core, data: Data):

	try:
		with files.transaction() as t:
			t.append(data)
			assert len(t) == 0
			raise KeyError
	except KeyError:
		assert not len(files)

	with files.transaction() as t:
		t.append(data)
		assert len(t) == 0
	assert len(files) == 1


def test_transaction_append_many(files: Files.Core, data: Data):

	try:
		with files.transaction() as t:
			for i in range(3):
				t.append(Data(value=data.value + str(i).encode()))
				assert len(t) == 0
			raise KeyError
	except KeyError:
		assert not len(files)

	with files.transaction() as t:
		for i in range(3):
			t.append(Data(value=data.value + str(i).encode()))
			assert len(t) == 0
	assert len(files) == 3