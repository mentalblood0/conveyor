import sqlalchemy



columns = lambda: (
	sqlalchemy.Column('value',       sqlalchemy.Integer(), nullable = False, primary_key = True, autoincrement = 'auto'),
	sqlalchemy.Column('description', sqlalchemy.Text(),    nullable = False, unique      = True)
)