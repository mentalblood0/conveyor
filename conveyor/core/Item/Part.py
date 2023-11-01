import dataclasses

from . import Item


@dataclasses.dataclass(frozen=True, kw_only=True)
class Part:
    type_: Item.Type | None = None
    status_: Item.Status | None = None
    data_: Item.Data | None = None
    digest_: Item.Data.Digest | None = None
    metadata_: Item.Metadata | None = None
    chain_: Item.Chain | None = None
    created_: Item.Created | None = None
    reserver_: Item.Reserver | None = None

    def __post_init__(self):
        match self.data_:
            case Item.Data():
                if self.digest_ is None:
                    return self.data_.digest
                elif self.data_.digest != self.digest_:
                    raise ValueError("Data digest not match separate digest")
            case None:
                pass

    @property
    def item(self) -> Item:
        return Item(
            type=self.type,
            status=self.status,
            data=self.data,
            metadata=self.metadata,
            chain=self.chain,
            created=self.created,
            reserver=self.reserver,
        )

    @property
    def type(self) -> Item.Type:
        assert self.type_ is not None, "Item part has no field `type` yet"
        return self.type_

    @property
    def status(self) -> Item.Status:
        assert self.status_ is not None, "Item part has no field `status` yet"
        return self.status_

    @property
    def data(self) -> Item.Data:
        assert self.data_ is not None, "Item part has no field `data` yet"
        return self.data_

    @property
    def digest(self) -> Item.Data.Digest:
        assert self.digest_ is not None, "Item part has no field `digest` yet"
        return self.digest_

    @property
    def metadata(self) -> Item.Metadata:
        assert self.metadata_ is not None, "Item part has no field `metadata` yet"
        return self.metadata_

    @property
    def chain(self) -> Item.Chain:
        assert self.chain_ is not None, "Item part has no field `chain` yet"
        return self.chain_

    @property
    def created(self) -> Item.Created:
        assert self.created_ is not None, "Item part has no field `created` yet"
        return self.created_

    @property
    def reserver(self) -> Item.Reserver:
        assert self.reserver_ is not None, "Item part has no field `reserver` yet"
        return self.reserver_
