import os

from .. import OutputProvider



class FileOutputProvider(OutputProvider):

	def __init__(self, path):
		self.path = path
	
	def set(self, new_data):

		try:
			with open(self.path, 'wb') as f:
				f.write(new_data)
			return new_data
		except FileNotFoundError:
			return None
	
	def create(self):
		os.mknod(self.path)



import sys
sys.modules[__name__] = FileOutputProvider