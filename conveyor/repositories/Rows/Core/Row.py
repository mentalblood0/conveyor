import typing
import pydantic

from ....core import Item, Transforms

from .Enum import Enum
from .Connect import Connect



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

	def dict_(self, transform: Transforms.Safe[Item.Key, str], connect: Connect, table: str, skip: set[str] = set()) -> dict[str, Item.Metadata.Value]:

		result: dict[str, Item.Metadata.Value] = {}

		if 'chain' not in skip:
			result['chain'] = self.chain
		status = Enum(
			name_ = Item.Key('status'),
			transform = transform
		)
		if status.name not in skip:
			result[status.name] = status.Int(connect, table)(self.status.value)
		if 'digest' not in skip:
			result['digest'] = self.digest.string
		if 'created' not in skip:
			result['created'] = self.created.value
		if 'reserver' not in skip:
			result['reserver'] = self.reserver.value

		for word, value in self.metadata.value.items():
			if word.value not in skip:
				match value:
					case Item.Metadata.Enumerable():
						e = Enum(
							name_     = word,
							transform = transform
						)
						result[e.name] = e.Int(connect, table)(value.value)
					case _:
						result[word.value] = value

		return result

	def sub(self, another: 'Row', transform: Transforms.Safe[Item.Key, str], connect: Connect, table: str,) -> dict[str, Item.Metadata.Value]:

		skip: set[str] = set()

		if self.status == another.status:
			skip.add('status')
		if self.digest == another.digest:
			skip.add('digest')
		if self.chain == another.chain:
			skip.add('chain')
		if self.created == another.created:
			skip.add('created')
		if self.reserver == another.reserver:
			skip.add('reserver')

		skip |= {
			k.value
			for k in self.metadata.value.keys()
			if self.metadata.value[k] == another.metadata.value[k]
		}

		return self.dict_(transform, connect, table, skip)