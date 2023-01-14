import pytest
import pydantic

from conveyor.core.Item import Data
from conveyor.repositories import Files

from ..common import *



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
	with pytest.raises(KeyError):
		del files[data.digest]


@pydantic.validate_arguments
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


@pydantic.validate_arguments
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