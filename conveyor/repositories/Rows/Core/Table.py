import typing
import sqlalchemy
import sqlalchemy.exc

from .Fields import Field



def Table(
	connection: sqlalchemy.Connection,
	name:       str,
	fields:     typing.Iterable[Field]
) -> None:

		fields = (*fields,)

		try:

			table = sqlalchemy.Table(
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
					if not (i := f.index(table)) in table.indexes:
						i.create(bind = connection)

		except sqlalchemy.exc.NoSuchTableError:

			table = sqlalchemy.Table(
				name,
				sqlalchemy.MetaData(),
				*(f.column for f in fields)
			)
			table.create(bind = connection)

			for i in table.indexes - {f.index(table) for f in fields}:
				i.create(bind = connection)