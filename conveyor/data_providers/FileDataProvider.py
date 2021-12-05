from .. import DataProvider



class FileDataProvider(DataProvider):

	def __init__(self, path):
		self.path = path
	
	def get(self):
	
		content = None
		with open(self.path, 'rb') as f:
			content = f.read()
	
		return content
	
	def set(self, new_data):
		with open(self.path, 'wb') as f:
			f.write(new_data)