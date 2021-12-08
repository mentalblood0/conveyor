from growing_tree_base import *

from .. import OutputProvider, DbItemTypeInterface, ComplexDataProvider
from . import FileOutputProvider



class MetadataOutputProvider(OutputProvider):

	def __init__(self, db_item_type_interface, id):
		self.db_item_type_interface = db_item_type_interface
		self.id = id

	def get(self):
		return self.db_item_type_interface.getById(self.id)


class ItemOutputProvider(OutputProvider):

	def __init__(self, dir_tree_root_path, *args, **kwargs):
		self.db_item_type_interface = DbItemTypeInterface(*args, **kwargs)
		self.dir_tree_root_path = dir_tree_root_path
		self.id = None
	
	def create(self, text, metadata):

		file_path = saveToDirTree(
			text, 
			self.dir_tree_root_path,
			base_file_name=f'{self.db_item_type_interface.item_type_name}.xml'
		)

		filtered_metadata = {
			k: v
			for k, v in metadata.items()
			if not k in ['id']
		}

		return self.db_item_type_interface.add(filtered_metadata | {
			'status': metadata['status'],
			'file_path': file_path
		})

	def set(self, new_fields):
		return self.db_item_type_interface.setById(self.id, new_fields)



import sys
sys.modules[__name__] = ItemOutputProvider