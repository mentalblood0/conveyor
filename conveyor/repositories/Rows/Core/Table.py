import typing
import pydantic
import sqlalchemy
import sqlalchemy.exc

from .Fields import Field



@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
def Table(
	connection: sqlalchemy.Connection,
	name:       str,
	fields_:    typing.Iterable[Field]
) -> sqlalchemy.Table:

		fields_ = (*fields_,)

		try:

			result = sqlalchemy.Table(
				name,
				sqlalchemy.MetaData(),
				*(f.column for f in fields_)
			)

			current_columns = {
				c['name']
				for c in sqlalchemy.inspect(connection).get_columns(name)
			}

			for f in fields_:
				if f.db_name not in current_columns:
					connection.execute(sqlalchemy.sql.text(f'ALTER TABLE {name} ADD {f.column.name} {f.column.type}'))
					if not (i := f.index(result)) in result.indexes:
						i.create(bind = connection)

		except sqlalchemy.exc.NoSuchTableError:

			result = sqlalchemy.Table(
				name,
				sqlalchemy.MetaData(),
				*(f.column for f in fields_)
			)
			result.create(bind = connection)

			for i in result.indexes - {f.index(result) for f in fields_}:
				i.create(bind = connection)


		return result