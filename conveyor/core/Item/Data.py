import hashlib
import pydantic

from .Digest import Digest



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Data:

	Digest = Digest

	value: pydantic.StrictBytes
	test: Digest | None = None

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

	@pydantic.validate_arguments
	def __eq__(self, another: object) -> bool:
		match another:
			case Data():
				return self.value == another.value
			case _:
				return False