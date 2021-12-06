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
	
	def create(self, status, text, fields):

		file_path = saveToDirTree(
			text, 
			self.dir_tree_root_path,
			base_file_name='undefined.xml'
		)

		return self.db_item_type_interface.add(fields | {
			'status': status,
			'file_path': file_path
		})

	def set(self, new_fields):
		return self.db_item_type_interface.setById(self.id, new_fields)



import sys
sys.modules[__name__] = ItemOutputProvider