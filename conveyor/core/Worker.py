import colorama
import traceback
from logama import log
from abc import ABCMeta, abstractmethod

from . import Item, Receiver



class Worker(Receiver, metaclass=ABCMeta):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.processItem = self.repository.transaction(self.processItem)

	@abstractmethod
	def processItem(self, item: Item) -> int | None:
		pass

	def __call__(self) -> list[int]:

		result = []

		try:
			items = self.receiveItems()
		except Exception as e:
			log(f'{self.__class__.__name__}.receiveItems: {e}', colorama.Fore.RED)
			return result

		for i in items:

			try:
				i_result = self.processItem(i)
			except Exception as e:
				text = '\n'.join(traceback.format_exc().split('\n')[1:])
				log(f'{self.__class__.__name__}.processItem: \n{text}', colorama.Fore.RED)
				continue

			result.append(i_result)
		
		return result