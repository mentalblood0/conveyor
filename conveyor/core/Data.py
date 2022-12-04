from __future__ import annotations

import hashlib
import pydantic

from .Digest import Digest



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Data:

	value: pydantic.StrictBytes
	test: Digest | None = None

	@pydantic.validator('test')
	def test_correct(cls, test, values):
		if test is not None:
			if Data(value=values['value']).digest != test:
				raise ValueError('Provided digest is not correct')
		return test

	@property
	def digest(self) -> Digest:
		return Digest(
			value=hashlib.sha3_512(
				self.value
			).digest()
		)

	@property
	def string(self) -> str:
		return self.value.decode()

	def __eq__(self, another) -> bool:
		return self.value == another.value