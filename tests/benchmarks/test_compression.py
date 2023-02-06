import bz2
import lzma
import zlib
import zopfli
import pytest
import pathlib
import functools



@pytest.fixture
@functools.cache
def input_() -> bytes:
	return (pathlib.Path(__file__).parent / 'test_compression_data.td').read_bytes()


@pytest.mark.benchmark(group='compression')
def test_lzma_compress(benchmark, input_: bytes):
	result: bytes = benchmark(lzma.compress, data = input_, preset = lzma.PRESET_EXTREME)
	benchmark.extra_info['factor'] = len(input_) / len(result)


@pytest.mark.benchmark(group='decompression')
def test_lzma_decompress(benchmark, input_: bytes):
	benchmark(lzma.decompress, data = lzma.compress(input_, preset=lzma.PRESET_EXTREME))


@pytest.mark.benchmark(group='compression')
def test_bzip2_compress(benchmark, input_: bytes):
	result: bytes = benchmark(bz2.compress, data = input_, compresslevel = 9)
	benchmark.extra_info['factor'] = len(input_) / len(result)


@pytest.mark.benchmark(group='decompression')
def test_bzip2_decompress(benchmark, input_: bytes):
	benchmark(bz2.decompress, data = bz2.compress(input_, compresslevel = 9))


@pytest.mark.benchmark(group='compression')
def test_zlib_compress(benchmark, input_: bytes):
	result: bytes = benchmark(zlib.compress, input_, level = 9)
	benchmark.extra_info['factor'] = len(input_) / len(result)


@pytest.mark.benchmark(group='decompression')
def test_zlib_decompress(benchmark, input_: bytes):
	benchmark(zlib.decompress, zlib.compress(input_, level = 9))