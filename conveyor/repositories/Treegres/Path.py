import os
import pydantic



class Path(str):
	@pydantic.validate_arguments
	def __new__(C, value: str):
		return super().__new__(
			C,
			os.path.normpath(os.path.normcase(value))
		)