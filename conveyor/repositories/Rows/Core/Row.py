import typing
import pydantic

from ....core import Item

from .Enums import Enums



@pydantic.dataclasses.dataclass(frozen = True, kw_only = True)
class Row:

	type     : Item.Type
	status   : Item.Status

	digest   : Item.Data.Digest
	metadata : Item.Metadata

	chain    : str
	created  : Item.Created
	reserver : Item.Reserver

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

	def dict_(self, enums: Enums.Enums, skip: set[str] = set()) -> dict[str, Item.Value]:

		result: dict[str, Item.Value] = {}

		if 'status' not in skip:
			status = enums[(self.type, Item.Key('status'))]
			result[status.db_field] = status.Int(self.status)

		if 'chain' not in skip:
			result['chain'] = self.chain
		if 'digest' not in skip:
			result['digest'] = self.digest.string
		if 'created' not in skip:
			result['created'] = self.created.value
		if 'reserver' not in skip:
			result['reserver'] = self.reserver.value

		for key, value in self.metadata.value.items():
			if key.value not in skip:
				match value:
					case Item.Metadata.Enumerable():
						e = enums[(self.type, Item.Key(key.value))]
						result[e.db_field] = e.convert(value)
					case _:
						result[key.value] = value

		return result

	def sub(self, another: 'Row', enums: Enums.Enums) -> dict[str, Item.Value]:

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

		for k in self.metadata.value.keys():
			if k in another.metadata.value:
				if self.metadata.value[k] == another.metadata.value[k]:
					skip.add(k.value)

		return self.dict_(enums, skip)