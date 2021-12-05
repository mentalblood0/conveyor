from .. import DataProvider



class DbRowDataProvider(DataProvider):

	def __init__(self, table_provider):
		self.table_provider