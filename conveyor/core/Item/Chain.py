import typing
import pydantic

from .Data import Data



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Chain:

	ref: Data | pydantic.StrictStr
	test: str | None = None

	@pydantic.validator('test')
	def test_valid(cls, test: str | None, values) -> str | None:

		if test is not None:

			ref: Data | str = values['ref']
			correct: Chain | Data | str | None = None

			match ref:
				case Data():
					correct = Chain(ref=values['ref']).value
				case str():
					correct = ref
				case _ as unreachable:
					assert typing.assert_never(unreachable)

			if correct != test:
				raise ValueError(f'Provided chain value "{test}" is not correct (correct is "{correct}")')

		return test

	@property
	def value(self) -> str:
		match self.ref:
			case Data():
				return self.ref.digest.string
			case str():
				return self.ref
			case _ as unreachable:
				assert typing.assert_never(unreachable)

	def __eq__(self, another: 'Chain') -> bool:
		return self.value == another.value