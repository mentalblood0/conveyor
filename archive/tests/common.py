import pytest
import shutil
from peewee import SqliteDatabase, PostgresqlDatabase

from conveyor.repositories import Treegres



db = SqliteDatabase(':memory:')
# db = PostgresqlDatabase(
# 	'postgres',
# 	host='localhost',
# 	port='5432',
# 	user='postgres',
# 	password='5924'
# )
dir_tree_root_path = 'dir_tree'
repository = Treegres(db=db, dir_tree_root_path=dir_tree_root_path)


@pytest.fixture(autouse=True, scope='session')
def clearFiles():
	shutil.rmtree(dir_tree_root_path, ignore_errors=True)