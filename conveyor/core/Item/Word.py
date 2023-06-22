import re
import pydantic

from .Enumerable import Enumerable



@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class Word(Enumerable):

	value: pydantic.StrictStr

	@pydantic.validator('value')
	def value_valid(cls, value: pydantic.StrictStr) -> pydantic.StrictStr:
		if re.match(r'\w+', value) is None:
			raise ValueError('`Word` value must be word')
		return value