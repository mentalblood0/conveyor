import pydantic



class ItemId(int):

	@pydantic.validate_arguments
	def __new__(C, value: str | int):

		if type(value) == int:
			return super().__new__(C, value)

		elif type(value) == str:
			if not len(value):
				result_value = -1
			else:
				result_value = int(value)
			return super().__new__(C, result_value)