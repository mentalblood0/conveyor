from abc import ABCMeta, abstractmethod

from . import Item, Receiver



class Processor(Receiver, metaclass=ABCMeta):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.processItem = self.repository.transaction(self.processItem)

	@abstractmethod
	def processItem(self, item: Item) -> int | None:
		pass

	def handleException(self, item: Item, e: Exception | None, worker_name: str):
		pass

	def handleNoException(self, item: Item, worker_name: str):
		pass

	@property
	def name(self):
		return self.__class__.__name__

	def __call__(self) -> list[int]:

		result = []

		try:
			items = self.receiveItems()
		except Exception as e:
			self.handleException(i, e, self.name)
			return result

		for i in items:

			try:
				i_result = self.processItem(i)
			except Exception as e:
				self.handleException(i, e, self.name)
				continue
			self.handleNoException(i, self.name)

			result.append(i_result)

		self.unreserve()

		return result