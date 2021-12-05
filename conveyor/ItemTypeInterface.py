from . import ItemType



class ItemTypeInterface:

	def __init__(self, db, item_type_name, data_fields):
		self.db = db
		self.item_type = ItemType(db, item_type_name, data_fields)
	
	def drop(self):
		return self.db.drop_tables([self.item_type])
	
	def create(self):
		return self.db.create_tables([self.item_type])
	
	def add(self, fields):
		
		if not self.item_type.table_exists():
			self.create()
		
		return self.item_type(**fields).save()
	
	def setStatus(self, id, new_status):
		return self.item_type.update(status=new_status).where(self.item_type.id==id).execute()
	
	def get(self, status):

		if not self.item_type.table_exists():
			return None
		
		first_item = self.item_type.select().where(self.item_type.status==status).first()
		if first_item == None:
			return None
		
		return first_item.__data__
	
	def delete(self, id):
		return self.item_type.delete().where(self.item_type.id==id).execute()



import sys
sys.modules[__name__] = ItemTypeInterface