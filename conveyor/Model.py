from peewee import Model as Model_
from playhouse.reflection import generate_models



class Model(Model_):

	def __new__(C, db, name, columns=None):

		name = name.lower()

		if not columns:
			models = generate_models(db, table_names=[name])
			if models:
				return models[name]

		else:
			result = type(
				name,
				(Model_,),
				{
					'Meta': type('Meta', (), {'database': db})
				} | columns
			)
			if not result.table_exists():
				with db.transaction():
					try:
						db.create_tables([result])
					except Exception as e:
						pass
			
			return result