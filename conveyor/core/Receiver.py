import socket
import threading
from abc import ABCMeta

from . import Item, Repository



class Receiver(metaclass=ABCMeta):

	input_type: str
	input_status: str

	receive_fields: list[str]=[]

	def __init__(self, repository: Repository, limit: int = 64) -> None:
		
		self.repository = repository
		self.limit = limit

		self.id = self.composeId()

	def composeId(self):
		return '_'.join([
			socket.gethostbyname(socket.gethostname()),
			str(threading.get_ident())
		])
	
	def reserve(self):
		return self.repository.reserve(
			type=self.input_type,
			status=self.input_status,
			id=self.id,
			limit=self.limit
		)
	
	def unreserve(self):
		return self.repository.unreserve(
			type=self.input_type,
			status=self.input_status,
			id=self.id
		)

	def receiveItems(self) -> list[Item]:

		self.reserve()

		return self.repository.get(
			self.input_type,
			where={'status': self.input_status},
			fields=self.receive_fields,
			limit=self.limit
		)