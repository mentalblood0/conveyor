from ..providers import FileProvider
from .. import InputProvider, OutputProvider, DbItemTypeInterface, ComplexDataProvider



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

	def delete(self):
		raise NotImplemented


class MetadataProvider(InputProvider, OutputProvider):

	def __init__(self, db_item_type_interface, id):
		self.db_item_type_interface = db_item_type_interface
		self.id = id

	def create(self):
		raise NotImplemented

	def get(self):
		return {
			k: MetadataFieldProvider(self.db_item_type_interface, self.id, k)
			for k in self.db_item_type_interface.getFieldsNames()
		}

	def set(self, new_data):

		data = self.get()

		for k, v in new_data:
			data[k].set(v)

	def delete(self):
		self.db_item_type_interface.delete(self.id)


class ItemInputProvider(InputProvider):

	def __init__(self, *args, **kwargs):
		self.db_item_type_interface = DbItemTypeInterface(*args, **kwargs)

	def get(self, status=None):

		id = self.db_item_type_interface.getId(status)
		if id == None:
			return None

		metadata = MetadataProvider(self.db_item_type_interface, id)
		file_path = metadata.get()['file_path'].get()

		return ComplexDataProvider({
			'text': FileProvider(file_path),
			'metadata': metadata
		})



import sys
sys.modules[__name__] = ItemInputProvider