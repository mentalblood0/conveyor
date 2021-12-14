from dataclasses import dataclass



@dataclass
class Metadata:
	pass


@dataclass
class Item:

	id: str = ''
	type: str = 'undefined'
	status: str = 'created'
	chain_id: str = ''

	data: str = ''
	metadata: dict = None

	def __hash__(self):
		return hash('_'.join([
			self.type,
			self.status,
			self.data if type(self.data) == str else self.data.decode(),
			str(self.metadata)
		]))



import sys
sys.modules[__name__] = Item