from peewee import *



def BaseModel(db):
	return type(
		'BaseModel_',
		(Model,),
		{'Meta': type('Meta', (), {'database': db})}
	)


def DbItemType_(db):
	return type(
		'DbItemType__',
		(BaseModel(db),),
		{'status': CharField()}
	)


def DbItemType(db, item_type_name, data_fields):
	return type(
		item_type_name.capitalize(),
		(DbItemType_(db),),
		data_fields | {'status': CharField(default='created')}
	)



import sys
sys.modules[__name__] = DbItemType