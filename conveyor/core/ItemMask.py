import pydantic

from .Item import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class ItemMask:

	type:        Item.Type
	status:      Item.Status      | None = None
	digest:      Item.Data.Digest | None = None
	data:        Item.Data        | None = None
	metadata:    Item.Metadata    | None = None
	chain:       Item.Chain       | None = None
	created:     Item.Created     | None = None
	reserver:    Item.Reserver    | None = None

	@pydantic.validator('data')
	def data_correct(cls, data: Item.Data | None, values: dict) -> Item.Data | None:
		if data is not None:
			return Item.Data(
				value=data.value,
				test=values['digest']
			)

	@property
	def conditions(self) -> dict[str, Item.Value]:

		result: dict[str, Item.Value] = {}

		if self.type is not None:
			result['type'] = self.type.value
		if self.status is not None:
			result['status'] = self.status.value
		if self.data is not None:
			result['data'] = self.data.string
			result['digest'] = self.data.digest.string
		elif self.digest is not None:
			result['digest'] = self.digest.string

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