import base64
from blake3 import blake3
from functools import cached_property
from dataclasses import dataclass, field



class _Data(str):

	@cached_property
	def digest(self):
		d = blake3(self.encode('utf8')).digest()
		return base64.b64encode(d).decode('ascii')


def Data(s: str, digest: str=None):
	
	result = _Data(s)
	if digest:
		if result.digest != digest:
			raise Exception(f"Cannot create data: digest invalid: '{result.digest}' != '{digest}'")
	
	return result


@dataclass
class Item:

	id: str = ''
	type: str = 'undefined'
	status: str = 'created'
	chain_id: str = ''
	worker: str = ''

	data: _Data = field(default_factory=Data)
	metadata: dict = None

	def __post_init__(self):
		if type(self.data) != _Data:
			self.data = Data(self.data)