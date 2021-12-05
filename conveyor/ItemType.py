from peewee import *



def BaseModel(db):
	return type(
		'BaseModel_',
		(Model,),
		{'Meta': type('Meta', (), {'database': db})}
	)


def ItemType_(db):
	return type(
		'ItemType__',
		(BaseModel(db),),
		{'status': CharField()}
	)


def ItemType(db, item_type_name, data_fields):
	return type(
		item_type_name.capitalize(),
		(ItemType_(db),),
		data_fields | {'status': CharField(default='created')}
	)



import sys
sys.modules[__name__] = ItemType