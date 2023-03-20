import random
import pytest
import hashlib
from blake3 import blake3
import pytest_benchmark.plugin



@pytest.fixture
def input_size() -> int:
	return 100


@pytest.fixture
def input_(input_size: int) -> bytes:
	return ''.join(
		random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*(){}[]')
		for _ in range(input_size * 1024)
	).encode()


def blake3_digest(i: bytes) -> bytes:
	return blake3(i, max_threads=blake3.AUTO).digest()


@pytest.mark.benchmark(group='digest')
def test_blake3(benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes):
	benchmark(blake3_digest, input_)


def sha3_512_digest(i: bytes) -> bytes:
	return hashlib.sha3_512(i).digest()


@pytest.mark.benchmark(group='digest')
def test_sha3_512(benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes):
	benchmark(sha3_512_digest, input_)


def sha3_256_digest(i: bytes) -> bytes:
	return hashlib.sha3_256(i).digest()


@pytest.mark.benchmark(group='digest')
def test_sha3_256(benchmark: pytest_benchmark.plugin.BenchmarkFixture, input_: bytes):
	benchmark(sha3_256_digest, input_)