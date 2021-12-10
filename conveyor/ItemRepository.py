from abc import ABCMeta, abstractmethod



class ItemRepository(metaclass=ABCMeta):

	@abstractmethod
	def save(self, item):
		pass

	@abstractmethod
	def get(self, type, status):
		pass

	@abstractmethod
	def delete(self, id):
		pass



import sys
sys.modules[__name__] = ItemRepository