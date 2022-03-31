import os



class Path(str):
	def __new__(C, value):
		return super().__new__(
			C,
			os.path.normpath(os.path.normcase(value))
		)