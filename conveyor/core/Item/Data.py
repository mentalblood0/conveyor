import typing
import hashlib
import pydantic
import dataclasses

from .Digest import Digest



@pydantic.validate_arguments
def default_algorithm(input_: bytes) -> bytes:
	return hashlib.sha3_512(input_).digest()


@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Data:

	Digest = Digest

	value     : pydantic.StrictBytes
	test      : Digest | None                   = dataclasses.field(default=None, compare=False)
	algorithm : typing.Callable[[bytes], bytes] = default_algorithm

	@pydantic.validator('test')
	def test_valid(cls, test: Digest | None, values: dict[str, pydantic.StrictBytes]) -> Digest | None:
		if test is not None:
			correct = Data(value=values['value']).digest
			if correct != test:
				raise ValueError(f'Provided digest "{test}" is not correct (correct is "{correct}")')
		return test

	@property
	def digest(self) -> Digest:
		return Digest(self.algorithm(self.value))

	@property
	def string(self) -> str:
		return self.value.decode()