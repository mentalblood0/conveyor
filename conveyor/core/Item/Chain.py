import pydantic

from .Data import Data



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Chain:

	ref: Data
	test: str | None = None

	@pydantic.validator('test')
	def test_correct(cls, test: str | None, values) -> str | None:
		if test is not None:
			correct = Chain(ref=values['ref']).value
			if correct != test:
				raise ValueError(f'Provided chain value "{test}" is not correct (correct is "{correct}")')
		return test

	@property
	def value(self) -> str:
		return self.ref.digest.string

	def __eq__(self, another: 'Chain') -> bool:
		return self.value == another.value