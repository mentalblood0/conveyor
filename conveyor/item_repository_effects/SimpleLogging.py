import sys
from loguru import logger
from threading import Lock

from .. import ItemRepositoryEffect



@lambda C: C()
class lock:

	def __init__(self):
		self.lock = Lock()
	
	def __call__(self):
		return self.lock


class SimpleLogging(ItemRepositoryEffect):

	def __init__(
		self,
		sink=sys.stderr,
		format: str='{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{message}</level>',
		remove_default_handler=True
	):

		if remove_default_handler:
			try:
				logger.remove(0)
			except ValueError:
				pass

		filter = lambda r: 'conveyor' in r['extra']
		with lock():
			
			if all([
				(not h._filter) or
				(h._filter.__code__.co_code != filter.__code__.co_code)
				for h in logger._core.handlers.values()
			]):
				logger.add(sink, format=format, filter=filter)
			
			for h in logger._core.handlers.values():
					if not h._filter:
						h._filter = lambda r: not 'conveyor' in r['extra']
		
		self.logger = logger.bind(conveyor='')

	def create(self, item):
		self.logger.success(f'-> {item.type}::{item.status}')
	
	def update(self, type, id, item):
		self.logger.info(f'{type}::?::{id} -> {type}::{item.status}')

	def delete(self, type, id):
		self.logger.debug(f'{type}::?::{id} ->')