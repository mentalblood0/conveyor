from peewee import Model as Model_
from playhouse.reflection import generate_models



def Model(db, name, columns=None):

	if not columns:
		models = generate_models(db, table_names=[name])
		return models[name] if models else None

	else:
		return type(
			name,
			(Model_,),
			{
				'Meta': type('Meta', (), {'database': db})
			} | columns
		)



import sys
sys.modules[__name__] = Model