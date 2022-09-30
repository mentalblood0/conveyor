import socket
import base64
import pydantic
from abc import ABCMeta

from ..common import ItemId
from . import Item, Repository, composeChainId, uuid7



def getSelfIP():

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.settimeout(0)

	try:
		# doesn't even have to be reachable
		s.connect(('10.255.255.255', 1))
		result = s.getsockname()[0]
	except Exception:
		result = '127.0.0.1'
	finally:
		s.close()

	return result


def composeReceiverId() -> str:
	u = uuid7()
	return base64.b64encode(
		b''.join([
			bytearray(int(n) for n in getSelfIP().split('.')),
			u.to_bytes(((u.bit_length() + 7) // 8), byteorder='big')
		])
	)


class Receiver(metaclass=ABCMeta):

	input_type: str
	input_status: str

	receive_fields: list[str]=[]

	@pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
	def __init__(self, repository: Repository, limit: int = 256) -> None:
		
		self.repository = repository
		self.limit = limit

		self.id = composeReceiverId()

	def reserve(self):
		return self.repository.reserve(
			type=self.input_type,
			status=self.input_status,
			id=self.id,
			limit=self.limit
		)

	def unreserve(self, ids: list[ItemId]):
		return self.repository.unreserve(
			type=self.input_type,
			ids=ids
		)

	def receiveItems(self) -> list[Item]:

		self.reserve()

		if len(self.receive_fields):
			receive_fields = self.receive_fields + [
				'id',
				'data_digest',
				'chain_id',
				'status'
			]
		else:
			receive_fields = self.receive_fields

		return self.repository.get(
			self.input_type,
			where={'status': self.input_status},
			fields=receive_fields,
			limit=self.limit,
			reserved_by=self.id
		)