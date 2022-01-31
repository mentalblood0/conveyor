from dataclasses import dataclass


@dataclass
class Item:

	id: str = ''
	chain_id: str = ''
	type: str = ''
	status: str = ''
	worker: str = ''

	data: str = ''
	data_digest: str = ''

	metadata: dict = None