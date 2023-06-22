import pydantic

from ..Item import Item



@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Mask:

	type     : Item.Type
	status   : Item.Status      | None = None
	data     : Item.Data        | None = None
	metadata : Item.Metadata    | None = None
	chain    : Item.Chain       | None = None
	created  : Item.Created     | None = None
	reserver : Item.Reserver    | None = None