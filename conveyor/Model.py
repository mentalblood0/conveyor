from peewee import Model as Model_
from playhouse.reflection import generate_models



def Model(db, name, columns=None):

	name = name.lower()

	if not columns:
		models = generate_models(db, table_names=[name])
		if models:
			return models[name]

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