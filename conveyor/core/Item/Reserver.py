import uuid
import base64
import dataclasses



@dataclasses.dataclass(frozen = True, kw_only = True)
class Reserver:

	exists : bool
	value  : str  = dataclasses.field(default_factory = lambda: base64.b64encode(uuid.uuid4().bytes).decode('ascii'))