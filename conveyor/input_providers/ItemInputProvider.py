import json

from .. import InputProvider, OutputProvider, DbItemTypeInterface, ComplexDataProvider
from . import FileInputProvider



class MetadataFieldProvider(InputProvider, OutputProvider):

	def __init__(self, db_item_type_interface, id, field_name):
		self.db_item_type_interface = db_item_type_interface
		self.id = id
		self.field_name = field_name
	
	def get(self):
		return self.db_item_type_interface.getField(self.id, self.field_name)

	def set(self, new_value):
		return self.db_item_type_interface.setById(self.id, {
			self.field_name: new_value
		})
	
	def create(self):
		raise NotImplemented


class MetadataInputProvider(InputProvider):

	def __init__(self, db_item_type_interface, id):
		self.db_item_type_interface = db_item_type_interface
		self.id = id
	
	def get(self):
		return {
			k: MetadataFieldProvider(self.db_item_type_interface, self.id, k)
			for k in self.db_item_type_interface.getFieldsNames() - {'file_path'}
		}


class ItemInputProvider(InputProvider):

	def __init__(self, *args, **kwargs):
		self.db_item_type_interface = DbItemTypeInterface(*args, **kwargs)

	def get(self, status):

		id = self.db_item_type_interface.getId(status)
		if id == None:
			return None
		file_path = self.db_item_type_interface.getField(id, 'file_path')

		return ComplexDataProvider({
			'text': FileInputProvider(file_path),
			'metadata': MetadataInputProvider(self.db_item_type_interface, id)
		})



import sys
sys.modules[__name__] = ItemInputProvider