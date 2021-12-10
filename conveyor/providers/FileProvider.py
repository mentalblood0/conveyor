import os

from .. import InputProvider, OutputProvider



class FileInputProvider(InputProvider, OutputProvider):

	def __init__(self, path):
		self.path = path
	
	def create(self):
		self.set('')
	
	def get(self):
		with open(self.path, 'rb') as f:
			content = f.read()
		return content
	
	def set(self, data):
		with open(self.path, 'wb') as f:
			f.write(data)
		return data

	def delete(self):
		os.remove(self.path)



import sys
sys.modules[__name__] = FileInputProvider