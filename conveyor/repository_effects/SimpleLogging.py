import sys
from loguru import logger
from threading import Lock

from .. import RepositoryEffect



@lambda C: C()
class lock:

	def __init__(self):
		self.lock = Lock()
	
	def __call__(self):
		return self.lock


class SimpleLogging(RepositoryEffect):

	def __init__(
		self,
		sink=sys.stderr,
		colors={
			'create': 'green',
			'update': 'blue',
			'delete': 'red'
		},
		remove_default_handler=True
	):

		if remove_default_handler:
			try:
				logger.remove(0)
			except ValueError:
				pass
		
		self.loggers = {}
		with lock():

			for h in logger._core.handlers.values():
				if not h._filter:
					h._filter = lambda r: not 'conveyor' in r['extra']

			for action in ['create', 'update', 'delete']:
				
				filter = eval(f"lambda r: ('conveyor' in r['extra']) and (r['extra']['conveyor'] == '{action}')")
				
				if all([
					(not h._filter) or
					(h._filter.__code__.co_consts != filter.__code__.co_consts)
					for h in logger._core.handlers.values()
				]):
					logger.add(
						sink,
						format=f'{{time:YYYY-MM-DD HH:mm:ss.SSS}} | <{colors[action]}>{{message}}</{colors[action]}>',
						filter=filter
					)
				
				self.loggers[action] = logger.bind(conveyor=action)

	def create(self, item):
		self.loggers['create'].info(f'-> {item.type}::{item.status}')
	
	def update(self, type, id, item):
		self.loggers['update'].info(f'{type}::?::{id} -> {type}::{item.status}')

	def delete(self, type, id):
		self.loggers['delete'].info(f'{type}::?::{id} ->')