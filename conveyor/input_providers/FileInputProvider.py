from .. import InputProvider



class FileInputProvider(InputProvider):

	def __init__(self, path):
		self.path = path
	
	def get(self):
	
		try:
			with open(self.path, 'rb') as f:
				content = f.read()
			return content
		except FileNotFoundError:
			return None



import sys
sys.modules[__name__] = FileInputProvider