from peewee import SqliteDatabase, Database

from conveyor.repositories import Treegres



db = SqliteDatabase(':memory:')
dir_tree_root_path = 'dir_tree'
repository = Treegres(db=db, dir_tree_root_path=dir_tree_root_path)