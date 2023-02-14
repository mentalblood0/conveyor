import typing
import pydantic
import sqlalchemy
import sqlalchemy.exc

from .Fields import Field



class AlterNeeded(Exception):
	pass


@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def Table(
	connection: sqlalchemy.Connection,
	name:       str,
	fields:     typing.Iterable[Field]
) -> sqlalchemy.Table:

		fields = (*fields,)

		try:

			result = sqlalchemy.Table(
				name,
				sqlalchemy.MetaData(),
				*(f.column for f in fields)
			)

			current_columns = {
				c['name']
				for c in sqlalchemy.inspect(connection).get_columns(name)
			}

			for f in fields:
				if f.db_name not in current_columns:
					connection.execute(sqlalchemy.sql.text(f"ALTER TABLE {name} ADD COLUMN {f.column.name} {f.column.type}"))
					if not (i := f.index(result)) in result.indexes:
						i.create(bind = connection)

		except sqlalchemy.exc.NoSuchTableError:

			result = sqlalchemy.Table(
				name,
				sqlalchemy.MetaData(),
				*(f.column for f in fields)
			)
			result.create(bind = connection)

			for i in result.indexes - {f.index(result) for f in fields}:
				i.create(bind = connection)


		return result