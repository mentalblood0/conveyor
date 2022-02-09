import colorama
from logama import log
from abc import ABCMeta, abstractmethod

from . import Item, Receiver



class Processor(Receiver, metaclass=ABCMeta):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.processItem = self.repository.transaction(self.processItem)

	@abstractmethod
	def processItem(self, item: Item) -> Item | str | None:
		pass

	def __call__(self) -> list[Item]:

		result = []

		try:
			items = self.receiveItems()
		except Exception as e:
			log(f'{self.__class__.__name__}.receiveItems: {e}', colorama.Fore.LIGHTRED_EX)
			return result

		for i in items:
			try:
				i_result = self.processItem(i)
				result.append(i_result)
			except Exception as e:
				log(f'{self.__class__.__name__}.processItem: {e}', colorama.Fore.LIGHTRED_EX)
				continue
		
		return result