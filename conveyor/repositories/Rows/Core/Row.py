import typing
import pydantic

from ....core import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Row:

	type:     Item.Type
	status:   Item.Status

	digest:   Item.Data.Digest
	metadata: Item.Metadata

	chain:    str
	created:  Item.Created
	reserver: Item.Reserver

	@pydantic.validator('metadata')
	def metadata_valid(cls, metadata: Item.Metadata, values: dict[str, Item.Value | Item.Metadata.Value]) -> Item.Metadata:
		for k in metadata.value:
			if k.value in values:
				raise KeyError(f'Field name "{k.value}" reserved and can not be used in metadata')
		return metadata

	@classmethod
	@pydantic.validate_arguments
	def from_item(cls, item: Item) -> typing.Self:
		return Row(
			type     = item.type,
			status   = item.status,
			digest   = item.data.digest,
			chain    = item.chain.value,
			created  = item.created,
			reserver = item.reserver,
			metadata = item.metadata
		)

	@property
	def dict_(self) -> dict[str, Item.Metadata.Value]:
		return {
			'chain':    self.chain,
			'status':   self.status.value,
			'digest':   self.digest.string,
			'created':  self.created.value,
			'reserver': self.reserver.value,
			**{
				word.value: value
				for word, value in self.metadata.value.items()
			}
		}

	def __sub__(self, another: 'Row') -> dict[str, Item.Metadata.Value]:

		result: dict[str, Item.Metadata.Value] = {}

		if self.status != another.status:
			result['status'] = self.status.value
		if self.digest != another.digest:
			result['digest'] = self.digest.string
		if self.chain != another.chain:
			result['chain'] = self.chain
		if self.created != another.created:
			result['created'] = self.created.value
		if self.reserver != another.reserver:
			result['reserver'] = self.reserver.value

		result |= {
			k.value: v
			for k, v in self.metadata.value.items()
			if self.metadata.value[k] != another.metadata.value[k]
		}

		return result
