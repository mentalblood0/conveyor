from peewee import *



def DbItemType_(db):
	return type(
		'DbItemType__',
		(Model,),
		{
			'Meta': type('Meta', (), {'database': db}),
			'status': CharField()
		}
	)


def DbItemType(db, item_type_name, data_fields):
	return type(
		item_type_name.capitalize(),
		(DbItemType_(db),),
		data_fields | {'status': CharField(default='created')}
	)



import sys
sys.modules[__name__] = DbItemType