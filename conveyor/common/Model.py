from playhouse.reflection import generate_models
from playhouse.migrate import SqliteMigrator, PostgresqlMigrator, migrate
from peewee import Model as Model_, SqliteDatabase, PostgresqlDatabase, Database

from .ModelsCache import models_cache



def composeMigrator(db):

	if db.__class__ == SqliteDatabase:
		migrator_class = SqliteMigrator
	elif db.__class__ == PostgresqlDatabase:
		migrator_class = PostgresqlMigrator
	else:
		raise NotImplementedError(f'No migrator class for db class "{db.__class__}"')

	return migrator_class(db)


class Model(Model_):

	def __new__(C, db: Database, name: str, columns=None, uniques: list[tuple[str]]=None):

		name = name.lower()

		if name in models_cache:
			return models_cache[name]

		if not columns:
			models = generate_models(db, table_names=[name])
			if len(models):
				models_cache[name] = models[name]
				return models[name]

		else:

			result = type(
				name,
				(Model_,),
				{
					'Meta': type(
						'Meta',
						(),
						{
							'database': db,
							'indexes': tuple(
								(u, True)
								for u in uniques or []
							)
						}
					)
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

			models_cache[name] = result

			return result
