from peewee import Model as Model_, SqliteDatabase, PostgresqlDatabase
from playhouse.migrate import SqliteMigrator, PostgresqlMigrator, migrate
from playhouse.reflection import generate_models



def composeMigrator(db):

	migrator_class = None

	if db.__class__ == SqliteDatabase:
		migrator_class = SqliteMigrator
	elif db.__class__ == PostgresqlDatabase:
		migrator_class = PostgresqlMigrator

	return migrator_class(db)


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
					except Exception:
						pass

			else:

				current_columns = [
					c.name
					for c in db.get_columns(name)
				]
				migrator = composeMigrator(db)

				with db.atomic():
					migrate(*[
						# migrator.drop_column(name, column_name)
						# for column_name in current_columns
						# if (column_name != 'id') and (column_name not in columns)
					],*[
						migrator.add_column(name, column_name, columns[column_name])
						for column_name in columns
						if column_name not in current_columns
					])


			return result