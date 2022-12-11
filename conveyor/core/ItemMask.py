import pydantic

from .Item.Item import Item
from .Item.Data import Data
from .Chain import Chain



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class ItemMask:

	type:        Item.Type
	status:      Item.Status   | None = None
	data:        Data          | None = None
	metadata:    Item.Metadata | None = None
	chain:       Chain         | None = None
	created:     Item.Created  | None = None
	reserver:    Item.Reserver | None = None

	@property
	def conditions(self) -> dict[str, Item.Metadata.Value]:

		result: dict[str, Item.Metadata.Value] = {}

		if self.type is not None:
			result['type'] = self.type.value
		if self.status is not None:
			result['status'] = self.status.value
		if self.data is not None:
			result['data'] = self.data.string

		if self.metadata is not None:
			for k, v in self.metadata.value.items():
				result[k.value] = v

		if self.chain is not None:
			result['chain'] = self.chain.value
		if self.created is not None:
			result['created'] = self.created.value
		if self.reserver is not None:
			result['reserver'] = self.reserver.value

		return result