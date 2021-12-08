from . import DbItemType



class DbItemTypeInterface:

	def __init__(self, db, item_type_name, data_fields):
		self.db = db
		self.item_type = DbItemType(db, item_type_name, data_fields)
		self.item_type_name = item_type_name
	
	def drop(self):
		return self.db.drop_tables([self.item_type])
	
	def create(self):
		return self.db.create_tables([self.item_type])
	
	def add(self, fields):

		if not self.item_type.table_exists():
			self.create()

		result = self.item_type(**fields).save()
		return result
	
	def getById(self, id):

		item = self.item_type.select().where(self.item_type.id==id).first()
		if item == None:
			return None
		
		return item.__data__
	
	def setById(self, id, new_fields):
		return self.item_type.update(**new_fields).where(self.item_type.id==id).execute()

	def getStatus(self, id):

		item = self.item_type.select(self.item_type.status).where(self.item_type.id==id).first()
		if item == None:
			return None
		
		return item.__data__
	
	def getField(self, id, field_name):

		item = self.item_type.select(getattr(self.item_type, field_name)).where(self.item_type.id==id).first()
		if item == None:
			return None
		
		return item.__data__[field_name]
	
	def setStatus(self, id, new_status):
		return self.item_type.update(status=new_status).where(self.item_type.id==id).execute()

	def getId(self, status):

		if not self.item_type.table_exists():
			return None
		
		first_item = self.item_type.select(self.item_type.id).where(self.item_type.status==status).first()
		if first_item == None:
			return None
		
		return first_item.__data__['id']

	def get(self, status):

		if not self.item_type.table_exists():
			return None
		
		first_item = self.item_type.select().where(self.item_type.status==status).first()
		if first_item == None:
			return None
		
		return first_item.__data__

	def getFieldsNames(self):
		return self.item_type._meta.fields.keys() - {'id'}

	def delete(self, id):
		return self.item_type.delete().where(self.item_type.id==id).execute()



import sys
sys.modules[__name__] = DbItemTypeInterface