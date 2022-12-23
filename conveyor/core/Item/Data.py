import hashlib
import pydantic
import dataclasses

from .Digest import Digest



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Data:

	Digest = Digest

	value: pydantic.StrictBytes
	test: Digest | None = dataclasses.field(default=None, compare=False)

	@pydantic.validator('test')
	def test_valid(cls, test: Digest | None, values: dict[str, pydantic.StrictBytes]) -> Digest | None:
		if test is not None:
			correct = Data(value=values['value']).digest
			if correct != test:
				raise ValueError(f'Provided digest "{test}" is not correct (correct is "{correct}")')
		return test

	@property
	def digest(self) -> Digest:
		return Digest(
			hashlib.sha3_512(
				self.value
			).digest()
		)

	@property
	def string(self) -> str:
		return self.value.decode()