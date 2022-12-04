from __future__ import annotations

import hashlib
import pydantic
import dataclasses

from .Digest import Digest



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Data:

	value: pydantic.StrictBytes
	digest: Digest | None = None
	test: Digest | None = None

	@pydantic.validator('digest')
	def digest_correct(cls, digest, values):
		if 'value' in values:
			if digest is None:
				return Digest(
					value=hashlib.sha3_512(
						values['value']
					).digest()
				)
			else:
				return digest

	@pydantic.validator('test')
	def test_correct(cls, test, values):
		if test is not None:
			if values['digest'] != test:
				raise ValueError('Provided digest is not correct')
		return test

	@property
	def string(self) -> str:
		return self.value.decode()

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __eq__(self, another) -> bool:
		return self.value == another.value