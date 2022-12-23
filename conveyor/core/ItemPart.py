import pydantic

from .Item import Item



class AccessError(Exception):
	pass


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class ItemPart:

	AccessError = AccessError

	type_:        Item.Type        | None = None
	status_:      Item.Status      | None = None
	data_:        Item.Data        | None = None
	digest_:      Item.Data.Digest | None = None
	metadata_:    Item.Metadata    | None = None
	chain_:       Item.Chain       | None = None
	created_:     Item.Created     | None = None
	reserver_:    Item.Reserver    | None = None

	@pydantic.validator('digest_')
	def digest__valid(cls, digest: Item.Data.Digest, values: dict[str, Item.Value]) -> Item.Data.Digest:

		match values['data_']:
			case Item.Data():
				if digest is None:
					return values['data_'].digest
				elif values['data_'].digest != digest:
					raise ValueError('Data digest not match separate digest')
			case None:
				pass
			case _:
				raise ValueError

		return digest

	@property
	def item(self) -> Item:
		return Item(
			type=self.type,
			status=self.status,
			data=self.data,
			metadata=self.metadata,
			chain=self.chain,
			created=self.created,
			reserver=self.reserver
		)

	@property
	def type(self) -> Item.Type:
		match self.type_:
			case None:
				raise AccessError('Item part has no field `type` yet')
			case _:
				return self.type_

	@property
	def status(self) -> Item.Status:
		match self.status_:
			case None:
				raise AccessError('Item part has no field `status` yet')
			case _:
				return self.status_

	@property
	def data(self) -> Item.Data:
		match self.data_:
			case None:
				raise AccessError('Item part has no field `data` yet')
			case _:
				return self.data_

	@property
	def digest(self) -> Item.Data.Digest:
		match self.digest_:
			case None:
				raise AccessError('Item part has no field `digest` yet')
			case _:
				return self.digest_

	@property
	def metadata(self) -> Item.Metadata:
		match self.metadata_:
			case None:
				raise AccessError('Item part has no field `metadata` yet')
			case _:
				return self.metadata_

	@property
	def chain(self) -> Item.Chain:
		match self.chain_:
			case None:
				raise AccessError('Item part has no field `chain` yet')
			case _:
				return self.chain_

	@property
	def created(self) -> Item.Created:
		match self.created_:
			case None:
				raise AccessError('Item part has no field `created` yet')
			case _:
				return self.created_

	@property
	def reserver(self) -> Item.Reserver:
		match self.reserver_:
			case None:
				raise AccessError('Item part has no field `reserver` yet')
			case _:
				return self.reserver_