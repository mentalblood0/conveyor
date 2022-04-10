import dataclasses



@dataclasses.dataclass
class Item:

	id: str = ''
	chain_id: str = ''

	type: str = ''
	status: str = ''

	data: str = ''
	data_digest: str = ''

	metadata: dict = dataclasses.field(default_factory=dict)

	reserved_by: str = ''