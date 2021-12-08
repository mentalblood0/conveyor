import uuid
from peewee import *
from datetime import datetime



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
		data_fields | {
			'status': CharField(default='created'),
			'chain_id': CharField(
				default=lambda: ' '.join([
					str(datetime.now()),
					uuid.uuid4().hex
				])
			)
		}
	)



import sys
sys.modules[__name__] = DbItemType