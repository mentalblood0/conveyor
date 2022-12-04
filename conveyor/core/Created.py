import datetime
import pydantic



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Created:

	value: datetime.datetime

	@pydantic.validator('value')
	def value_not_greater_then_now(cls, d):
		if d > datetime.datetime.utcnow():
			raise ValueError('`Created` value must not be greater then now')
		return d