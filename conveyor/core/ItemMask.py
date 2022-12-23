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
	def data_correct(cls, data: Item.Data | None, values: dict[str, Item.Value]) -> Item.Data | None:
		if data is not None:
			match values['digest']:
				case Item.Data.Digest():
					return Item.Data(
						value=data.value,
						test=values['digest']
					)
				case None:
					return data
				case _:
					raise ValueError('`digest_` must be of types `None` or `Digest`')