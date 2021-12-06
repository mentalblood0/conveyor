from .. import InputProvider, DbItemTypeInterface



class ItemInputProvider(InputProvider):

	def __init__(self, **kwargs):
		self.db_item_type_interface = DbItemTypeInterface(**kwargs)

	def get(self, **kwargs):
		return self.db_item_type_interface(**kwargs)



import sys
sys.modules[__name__] = ItemInputProvider