import os
from growing_tree_base import *

from .. import Command, Item, Repository



class Create(Command):

	def execute(self, text: str, dir_tree_root_path: str, base_file_name: str='.xml', *args, **kwargs) -> str:
		return saveToDirTree(
			text, 
			dir_tree_root_path,
			base_file_name=base_file_name
		)
	
	def _revert(self, result: str, *args, **kwargs):
		os.remove(result)


class Delete(Command):

	def execute(self, file_path: str, *args, **kwargs) -> int:
		return os.remove(file_path)
	
	def _revert(self, *args, **kwargs):
		pass



def get(file_path: str, *args, **kwargs) -> Item:

	with open(file_path, 'r', encoding='utf8') as f:
		file_content = f.read()

	return file_content


class FileRepository(Repository):

	subrepositories = {}

	commands = {
		'create': Create,
		'delete': Delete
	}

	queries = {
		'get': get
	}