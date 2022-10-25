import pydantic
import dataclasses
from datetime import datetime



@pydantic.dataclasses.dataclass(frozen=True)
class Item:

	id: str = ''
	chain_id: str = ''

	type: str = ''
	status: str = ''

	data: str = ''
	data_digest: str = ''

	date_created: datetime = dataclasses.field(default_factory=datetime.utcnow)
	date_updated: datetime = dataclasses.field(default_factory=datetime.utcnow)

	metadata: dict = dataclasses.field(default_factory=dict)

	reserved_by: str = None