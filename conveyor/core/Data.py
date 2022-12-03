from __future__ import annotations

import pydantic
import dataclasses
from blake3 import blake3

from .Digest import Digest



@pydantic.dataclasses.dataclass(frozen=True)
class Data:

	value: bytes
	test: dataclasses.InitVar[Digest | None] = None

	def __post_init__(self, test):
		if test is not None:
			assert self.digest == test

	@property
	def digest(self) -> Digest:
		return Digest(
			value=blake3(
				self.value,
				max_threads=blake3.AUTO
			).digest()
		)

	@property
	def string(self) -> str:
		return self.value.decode()

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __eq__(self, another) -> bool:
		return self.value == another.value