import peewee
import pydantic
import playhouse.migrate
import playhouse.reflection



class BaseModel(peewee.Model):
	status   = peewee.CharField(max_length=63, index=True),
	digest   = peewee.CharField(max_length=63, index=True),
	chain    = peewee.CharField(max_length=63, index=True),
	reserved = peewee.CharField(max_length=63, index=True, default=None, null=True)


@pydantic.validate_arguments
def composeMigrator(db: peewee.Database) -> playhouse.migrate.SchemaMigrator:

	if db.__class__ == peewee.SqliteDatabase:
		migrator_class = playhouse.migrate.SqliteMigrator
	elif db.__class__ == peewee.PostgresqlDatabase:
		migrator_class = playhouse.migrate.PostgresqlMigrator
	else:
		raise NotImplementedError(f'No migrator class for db class "{db.__class__}"')

	return migrator_class(db)


models_cache: dict[str, type[BaseModel]] = {}


@pydantic.validate_arguments
def Model(
	db: peewee.Database,
	name: str,
	columns: dict[str, peewee.Field] | None=None
) -> type[BaseModel]:

		name = name.lower()

		if not columns:

			if name in models_cache:
				return models_cache[name]

			models: dict[str, type[peewee.Model]] = playhouse.reflection.generate_models(db, table_names=[name])
			if len(models):
				models_cache[name] = models[name]
				return models[name]

			raise KeyError(f"No table with name '{name}' and columns {columns} found")

		else:

			class Result(BaseModel):
				class Meta:
					database = db

			for k, v in columns:
				Result._meta.add_field(k, v)

			if not Result.table_exists():

				with db.transaction():
					try:
						db.create_tables([Result])
					except Exception:
						pass

			else:

				current_columns = [
					c.name
					for c in db.get_columns(name)
				]
				migrator = composeMigrator(db)

				with db.atomic():
					playhouse.migrate.migrate(*[
						# migrator.drop_column(name, column_name)
						# for column_name in current_columns
						# if (column_name != 'id') and (column_name not in columns)
					],*[
						migrator.add_column(name, column_name, columns[column_name])
						for column_name in columns
						if column_name not in current_columns
					])

			models_cache[name] = Result

			return Result
