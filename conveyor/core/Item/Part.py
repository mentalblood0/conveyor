import dataclasses

from . import Item


class AccessError(BaseException):
    def __init__(self, field: str):
        self.message = f"Item part has no field `{field}` yet"

    def __str__(self) -> str:
        return self.message


@dataclasses.dataclass(frozen=True, kw_only=True)
class Part:
    AccessError = AccessError

    kind_: Item.Kind | None = None
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
            kind=self.kind,
            status=self.status,
            data=self.data,
            metadata=self.metadata,
            chain=self.chain,
            created=self.created,
            reserver=self.reserver,
        )

    @property
    def kind(self) -> Item.Kind:
        match self.kind_:
            case None:
                raise AttributeError(name="kind")
            case _:
                return self.kind_

    @property
    def status(self) -> Item.Status:
        match self.status_:
            case None:
                raise AttributeError(name="status")
            case _:
                return self.status_

    @property
    def data(self) -> Item.Data:
        match self.data_:
            case None:
                raise AttributeError(name="data")
            case _:
                return self.data_

    @property
    def digest(self) -> Item.Data.Digest:
        match self.digest_:
            case None:
                raise AttributeError(name="digest")
            case _:
                return self.digest_

    @property
    def metadata(self) -> Item.Metadata:
        match self.metadata_:
            case None:
                raise AttributeError(name="metadata")
            case _:
                return self.metadata_

    @property
    def chain(self) -> Item.Chain:
        match self.chain_:
            case None:
                raise AttributeError(name="chain")
            case _:
                return self.chain_

    @property
    def created(self) -> Item.Created:
        match self.created_:
            case None:
                raise AttributeError(name="created")
            case _:
                return self.created_

    @property
    def reserver(self) -> Item.Reserver:
        match self.reserver_:
            case None:
                raise AttributeError(name="reserver")
            case _:
                return self.reserver_
