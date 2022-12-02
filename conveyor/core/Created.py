import datetime
import pydantic



class Created(datetime.datetime):

	@pydantic.validate_arguments
	def __new__(cls, d: datetime.datetime):

		assert d <= datetime.datetime.utcnow()
		return d