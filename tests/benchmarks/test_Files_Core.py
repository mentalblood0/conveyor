import pytest
import typing
import pathlib
import pytest_benchmark.plugin

from tests.common import *

from conveyor.core.Item import Data



@pytest.fixture
def empty() -> Data:
	return Data(value = b'v')


@pytest.mark.benchmark(group='files')
def test_add_same_empty(benchmark: pytest_benchmark.plugin.BenchmarkFixture, files: Files.Core, empty: Data):
	benchmark(files.append, empty)
	files.clear()


@pytest.fixture
def big() -> Data:
	return Data(value = (pathlib.Path(__file__).parent / 'test_big_data.td').read_bytes())


@pytest.mark.benchmark(group='files')
def test_add_same_big(benchmark: pytest_benchmark.plugin.BenchmarkFixture, files: Files.Core, big: Data):
	benchmark(files.append, big)
	files.clear()


def append_different(files: Files.Core, data: Data) -> typing.Callable[[], None]:

	current_data = data

	def append():
		nonlocal current_data
		files.append(current_data)
		current_data = Data(value = current_data.value + b' ')

	return append


@pytest.mark.benchmark(group='files')
def test_add_different_big(benchmark: pytest_benchmark.plugin.BenchmarkFixture, files: Files.Core, big: Data):
	benchmark(append_different(files, big))
	files.clear()