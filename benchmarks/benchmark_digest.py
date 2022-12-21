import random
import hashlib
import functools
from blake3 import blake3
from sharpener_lite import Benchmark

from benchmarks.common import *



class WithRandomInput:

	def prepare(self):
		self.input_

	@functools.cached_property
	def input_(self) -> bytes:
		return ''.join(
			random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*(){}[]')
			for i in range(self.config.kwargs['input_size_kilobytes'] * 1024)
		).encode()


class blake3_(Benchmark, WithOutputMetrics, WithRandomInput):

	def run(self):
		return blake3(self.input_, max_threads=blake3.AUTO).digest()


class sha3_512(Benchmark, WithOutputMetrics, WithRandomInput):

	def prepare(self):
		self.input_

	@functools.cached_property
	def input_(self) -> bytes:
		return ''.join(
			random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*(){}[]')
			for i in range(self.config.kwargs['input_size_kilobytes'] * 1024)
		).encode()

	def run(self):
		return hashlib.sha3_512(
			self.input_
		).digest()


class sha3_256(Benchmark, WithOutputMetrics, WithRandomInput):

	def prepare(self):
		self.input_

	@functools.cached_property
	def input_(self) -> bytes:
		return ''.join(
			random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*(){}[]')
			for i in range(self.config.kwargs['input_size_kilobytes'] * 1024)
		).encode()

	def run(self):
		return hashlib.sha3_256(
			self.input_
		).digest()