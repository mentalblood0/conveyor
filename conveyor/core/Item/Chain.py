import pydantic

from .Data import Data



@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Chain:

	ref  : Data | pydantic.StrictStr
	test : str  | None               = None

	@pydantic.validator('test')
	def test_valid(cls, test: str | None, values: dict[str, Data | pydantic.StrictStr]) -> str | None:

		if test is not None:

			ref: Data | str = values['ref']

			match ref:
				case Data():
					correct = Chain(ref=values['ref']).value
				case str():
					correct = ref

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

	def __eq__(self, another: object) -> bool:
		match another:
			case Chain():
				return self.value == another.value
			case _:
				raise ValueError(f'Can not compare instance of type `Chain` with instance of type `{type(another)}`')