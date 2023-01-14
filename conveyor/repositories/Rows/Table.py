import pydantic
import sqlalchemy
import sqlalchemy.exc

from ...core import Item

from .Field import Field, base_fields



tables = sqlalchemy.MetaData()


@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def Table(
	connection: sqlalchemy.Connection,
	name:       Item.Type,
	metadata:   Item.Metadata
) -> sqlalchemy.Table:

		name = Item.Type(f'conveyor_{name.value.lower()}')

		with connection.begin_nested() as _:

			fields = {
				Field(name_ = n, value = None)
				for n in base_fields
			} | {
				Field(name_ = k, value = v)
				for k, v in metadata.value.items()
			}

			try:

				result = sqlalchemy.Table(
					name.value,
					sqlalchemy.MetaData(),
					*(f.column for f in fields)
				)

				current_columns = {
					c['name']
					for c in sqlalchemy.inspect(connection).get_columns(name.value)
				}

				for f in fields:
					if f.name not in current_columns:
						connection.execute(sqlalchemy.sql.text(f'ALTER TABLE {name.value} ADD {f.column.name} {f.column.type}'))
						if not (i := f.index(result)) in result.indexes:
							i.create(bind = connection)

			except sqlalchemy.exc.NoSuchTableError:

				result = sqlalchemy.Table(
					name.value,
					sqlalchemy.MetaData(),
					*(f.column for f in fields)
				)
				result.create(bind = connection)

				for i in result.indexes - {f.index(result) for f in fields}:
					i.create(bind = connection)


			return result
