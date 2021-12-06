from peewee import PostgresqlDatabase, CharField
from conveyor.input_providers import Item

from . import isXml



db = PostgresqlDatabase('postgres', user='postgres', password='5924', host='localhost', port=5432)

is_xml_transformer = isXml(
	input_provider=Item(
		dir_tree_root_path='dir_tree',
		type={
			'db': db,
			'name': 'PersonalizationRequest',
			'schema': {
				'message_id': CharField(),
				'file_path': CharField()
			}
		}
	)
)