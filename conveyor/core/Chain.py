import typing
import pydantic

from .Data import Data
from .Item import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Chain:

	ref: Data | Item
	test: str | None = None

	@pydantic.validator('test')
	def test_correct(cls, test, values):
		if test is not None:
			correct = Chain(ref=values['ref']).value
			if correct != test:
				raise ValueError(f'Provided chain value "{test}" is not correct (correct is "{correct}")')
		return test

	@property
	def value(self) -> str:
		match self.ref:
			case Data():
				return self.ref.digest.string
			case Item():
				return self.ref.chain.value
			case _ as unreachable:
				typing.assert_never(unreachable)

	def __eq__(self, another: 'Chain') -> bool:
		return self.value == another.value