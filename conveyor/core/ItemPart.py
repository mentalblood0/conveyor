import pydantic

from . import Item, Chain



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
	chain_:       Chain            | None = None
	created_:     Item.Created     | None = None
	reserved_:    Item.Reserved    | None = None
	reserver_:    Item.Reserver    | None = None

	@pydantic.validator('digest_')
	def digest__correct(cls, digest: Item.Data.Digest, values) -> Item.Data.Digest:
		if digest is None:
			if values['data_'] is not None:
				return values['data_'].digest
		else:
			if values['data_'] is not None:
				if values['data_'].digest != digest:
					raise ValueError('Data digest not match separate digest')
		return digest

	@pydantic.validator('chain_')
	def chain__correct(cls, chain_: Chain, values) -> Chain:
		if chain_ is not None:
			if values['data_'] is not None:
				return Chain(
					ref=values['data_'],
					test=chain_.value
				)
		return chain_

	@property
	def item(self) -> Item:
		return Item(
			type=self.type,
			status=self.status,
			data=self.data,
			metadata=self.metadata,
			chain=self.chain,
			created=self.created,
			reserved=self.reserved,
			reserver=self.reserver
		)

	@property
	def type(self) -> Item.Type:
		match self.type_:
			case None:
				raise AccessError('Field `type` not specified yet')
			case _:
				return self.type_

	@property
	def status(self) -> Item.Status:
		match self.status_:
			case None:
				raise AccessError('Field `status` not specified yet')
			case _:
				return self.status_

	@property
	def data(self) -> Item.Data:
		match self.data_:
			case None:
				raise AccessError('Field `data` not specified yet')
			case _:
				return self.data_

	@property
	def digest(self) -> Item.Data.Digest:
		match self.digest_:
			case None:
				raise AccessError('Field `digest` not specified yet')
			case _:
				return self.digest_

	@property
	def metadata(self) -> Item.Metadata:
		match self.metadata_:
			case None:
				raise AccessError('Field `metadata` not specified yet')
			case _:
				return self.metadata_

	@property
	def chain(self) -> Chain:
		match self.chain_:
			case None:
				raise AccessError('Field `chain` not specified yet')
			case _:
				return self.chain_

	@property
	def created(self) -> Item.Created:
		match self.created_:
			case None:
				raise AccessError('Field `created` not specified yet')
			case _:
				return self.created_

	@property
	def reserved(self) -> Item.Reserved:
		match self.reserved_:
			case None:
				raise AccessError('Field `reserved` not specified yet')
			case _:
				return self.reserved_

	@property
	def reserver(self) -> Item.Reserver:
		return self.reserver_