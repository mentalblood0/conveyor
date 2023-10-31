import bz2
import lzma
import zlib
import zopfli
import pytest
import pathlib
import functools
import brotlicffi
import pytest_benchmark.plugin


@pytest.fixture
@functools.cache
def input_() -> bytes:
    return (pathlib.Path(__file__).parent / "test_compression_data.td").read_bytes()


@pytest.mark.benchmark(group="compression")
def test_lzma_compress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    result: bytes = benchmark(lzma.compress, data=input_, preset=lzma.PRESET_EXTREME)
    benchmark.extra_info["factor"] = len(input_) / len(result)


@pytest.mark.benchmark(group="decompression")
def test_lzma_decompress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    benchmark(lzma.decompress, data=lzma.compress(input_, preset=lzma.PRESET_EXTREME))


@pytest.mark.benchmark(group="compression")
def test_bzip2_compress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    result: bytes = benchmark(bz2.compress, data=input_, compresslevel=9)
    benchmark.extra_info["factor"] = len(input_) / len(result)


@pytest.mark.benchmark(group="decompression")
def test_bzip2_decompress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    benchmark(bz2.decompress, data=bz2.compress(input_, compresslevel=9))


@pytest.mark.benchmark(group="compression")
def test_zlib_compress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    result: bytes = benchmark(zlib.compress, input_, level=9)
    benchmark.extra_info["factor"] = len(input_) / len(result)


@pytest.mark.benchmark(group="decompression")
def test_zlib_decompress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    benchmark(zlib.decompress, zlib.compress(input_, level=9))


@pytest.mark.benchmark(group="compression")
def test_zopfli_compress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    def compress(b: bytes) -> bytes:
        c = zopfli.ZopfliCompressor(zopfli.ZOPFLI_FORMAT_DEFLATE)
        return c.compress(b) + c.flush()

    result: bytes = benchmark(compress, input_)
    benchmark.extra_info["factor"] = len(input_) / len(result)


@pytest.mark.benchmark(group="decompression")
def test_zopfli_decompress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    def decompress(b: bytes) -> bytes:
        d = zopfli.ZopfliDecompressor(zopfli.ZOPFLI_FORMAT_DEFLATE)
        return d.decompress(b) + d.flush()

    c = zopfli.ZopfliCompressor(zopfli.ZOPFLI_FORMAT_DEFLATE)

    benchmark(decompress, c.compress(input_) + c.flush())


@pytest.mark.benchmark(group="compression")
def test_brotlicffi_compress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    def compress(b: bytes) -> bytes:
        c = brotlicffi.Compressor(mode=brotlicffi.MODE_TEXT)
        return c.process(b) + c.finish()

    result: bytes = benchmark(compress, input_)
    benchmark.extra_info["factor"] = len(input_) / len(result)


@pytest.mark.benchmark(group="decompression")
def test_brotlicffi_decompress(
    benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes
):
    def decompress(b: bytes) -> bytes:
        d = brotlicffi.Decompressor()
        return d.process(b) + d.finish()

    c = brotlicffi.Compressor(mode=brotlicffi.MODE_TEXT)

    benchmark(decompress, c.process(input_) + c.finish())
