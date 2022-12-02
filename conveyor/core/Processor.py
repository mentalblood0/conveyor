import abc
import pydantic

from . import Item, Receiver



class Processor(Receiver, metaclass=abc.ABCMeta):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.processItem = self.repository.transaction(self.process)

	@abc.abstractmethod
	@pydantic.validate_arguments
	def process(self, item: Item) -> None:
		pass

	@pydantic.validate_arguments
	def handleException(self, item: Item | None, e: Exception, worker: str) -> None:
		pass

	@pydantic.validate_arguments
	def handleNoException(self, item: Item) -> None:
		pass

	@property
	def name(self):
		return self.__class__.__name__

	def __call__(self) -> None:

		items = []

		try:
			items = self.receive()
		except Exception as e:
			self.handleException(None, e, self.name)

		for i in items:

			try:
				self.process(i)
			except Exception as e:
				self.handleException(i, e, self.name)
				continue

			self.unreserve(i)
			self.handleNoException(i)