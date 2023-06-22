import datetime
import pydantic



@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class Created:

	value: datetime.datetime

	@pydantic.validator('value')
	def value_valid(cls, value: datetime.datetime) -> datetime.datetime:
		if value > datetime.datetime.utcnow():
			raise ValueError('`Created` value must not be greater then now')
		return value