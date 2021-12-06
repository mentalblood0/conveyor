from .. import OutputProvider, DbItemTypeInterface



class ItemOutputProvider(OutputProvider):

	def __init__(self, **kwargs):
		self.db_item_type_interface = DbItemTypeInterface(**kwargs)

	def set(self, **kwargs):
		return self.setStatus()



import sys
sys.modules[__name__] = ItemOutputProvider