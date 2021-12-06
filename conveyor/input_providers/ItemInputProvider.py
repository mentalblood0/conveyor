from .. import InputProvider, OutputProvider, DbItemTypeInterface, ComplexDataProvider
from . import FileInputProvider



class MetadataInputProvider(InputProvider):

	def __init__(self, db_item_type_interface, id):
		self.db_item_type_interface = db_item_type_interface
		self.id = id

	def get(self):
		return self.db_item_type_interface.getById(self.id)


class StatusProvider(InputProvider, OutputProvider):

	def __init__(self, db_item_type_interface, id):
		self.db_item_type_interface = db_item_type_interface
		self.id = id

	def get(self):
		return self.db_item_type_interface.get(self.id)
	
	def set(self, new_value):
		return self.db_item_type_interface.setStatus(self.id, new_value)


class ItemInputProvider(InputProvider):

	def __init__(self, *args, **kwargs):
		self.db_item_type_interface = DbItemTypeInterface(*args, **kwargs)

	def get(self, status):

		item = self.db_item_type_interface.get(status)
		if item == None:
			return None

		return ComplexDataProvider({
			'status': StatusProvider(self.db_item_type_interface, item['id']),
			'file': FileInputProvider(item['file_path']),
			'metadata': MetadataInputProvider(self.db_item_type_interface, item['id'])
		})



import sys
sys.modules[__name__] = ItemInputProvider