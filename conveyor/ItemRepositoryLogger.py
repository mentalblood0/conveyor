from abc import ABCMeta, abstractmethod

from . import Item, ItemRepository



def sequence(functions):

	def new_f(*args, **kwargs):
		
		for f in functions[:-1]:
			f(*args, **kwargs)
		
		return functions[-1](*args, **kwargs)
	
	return new_f


class ItemRepositoryLogger(metaclass=ABCMeta):

	def install(self, repository: ItemRepository, *args, **kwargs) -> ItemRepository:
		
		for name in ['create', 'update', 'delete']:
			setattr(repository, name, sequence([
				getattr(self, name),
				getattr(repository, name)
			]))

	@abstractmethod
	def create(self, item: Item) -> None:
		pass

	@abstractmethod
	def update(self, type: str, id: str, item: Item) -> None:
		pass

	@abstractmethod
	def delete(self, id: str) -> None:
		pass
