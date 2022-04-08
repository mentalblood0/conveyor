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

	def handleException(self, e):
		text = ''.join(traceback.format_exception(e)[1:])
		log(f'{self.__class__.__name__}:\n{text}', colorama.Fore.RED)

	def __call__(self) -> list[int]:

		result = []

		try:
			items = self.receiveItems()
		except Exception as e:
			self.handleException(e)
			return result

		for i in items:

			try:
				i_result = self.processItem(i)
			except Exception as e:
				self.handleException(e)
				continue

			result.append(i_result)
		
		return result