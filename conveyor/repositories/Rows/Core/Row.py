import typing
import itertools
import dataclasses

from ....core import Item

from .Enums import Enums


@dataclasses.dataclass(frozen=True, kw_only=True)
class Row:
    kind: Item.Kind
    status: Item.Status

    digest: Item.Data.Digest
    metadata: Item.Metadata

    chain: str
    created: Item.Created
    reserver: Item.Reserver

    def __post_init__(self):
        if any(k.value in dir(self) for k in self.metadata):
            raise TypeError(
                f"Some fields from metadata {self.metadata} are "
                f"collide with reserved fields {dir(self)}"
            )

    @classmethod
    def from_item(cls, item: Item) -> typing.Self:
        return Row(
            kind=item.kind,
            status=item.status,
            digest=item.data.digest,
            chain=item.chain.value,
            created=item.created,
            reserver=item.reserver,
            metadata=item.metadata,
        )

    @dataclasses.dataclass(frozen=True, kw_only=True)
    class Dict:
        row: "Row"
        enums: Enums.Enums
        skip: set[
            typing.Literal["status", "digest", "chain", "created", "reserver"]
        ] = dataclasses.field(default_factory=set)

        def __call__(self):
            return dict[str, Item.Value]({key: value for key, value in self})

        def __iter__(self):
            return itertools.chain(
                self.status,
                self.chain,
                self.digest,
                self.created,
                self.reserver,
                self.metadata,
            )

        @property
        def status(self):
            if "status" not in self.skip:
                status = self.enums[(self.row.kind, Item.Key("status"))]
                yield (status.db_field, status.integer(self.row.status))

        @property
        def chain(self):
            if "chain" not in self.skip:
                yield ("chain", self.row.chain)

        @property
        def digest(self):
            if "digest" not in self.skip:
                yield ("digest", self.row.digest.string)

        @property
        def created(self):
            if "created" not in self.skip:
                yield ("created", self.row.created.value)

        @property
        def reserver(self):
            if "reserver" not in self.skip:
                yield ("reserver", self.row.reserver.value)

        @property
        def metadata(self):
            for key, value in self.row.metadata.items():
                if key.value not in self.skip:
                    match value:
                        case Item.Metadata.Enumerable():
                            e = self.enums[(self.row.kind, Item.Key(key.value))]
                            yield (e.db_field, e.convert(value))
                        case _:
                            yield (key.value, value)

    @dataclasses.dataclass(frozen=True, kw_only=True)
    class Skip:
        row: "Row"
        another: "Row"
        enums: Enums.Enums

        def __call__(self):
            return set(s for s in self)

        def __iter__(self):
            return itertools.chain(
                self.status, self.digest, self.chain, self.created, self.reserver
            )

        @property
        def status(self):
            if self.row.status == self.another.status:
                yield "status"

        @property
        def digest(self):
            if self.row.digest == self.another.digest:
                yield "digest"

        @property
        def chain(self):
            if self.row.chain == self.another.chain:
                yield "chain"

        @property
        def created(self):
            if self.row.created == self.another.created:
                yield "created"

        @property
        def reserver(self):
            if self.row.reserver == self.another.reserver:
                yield "reserver"

        @property
        def metadata(self):
            for k in self.row.metadata.keys():
                if k in self.another.metadata and (
                    self.row.metadata[k] == self.another.metadata[k]
                ):
                    yield k.value

    def sub(self, another: "Row", enums: Enums.Enums) -> dict[str, Item.Value]:
        return self.Dict(
            row=self,
            enums=enums,
            skip=self.Skip(row=self, another=another, enums=enums)(),
        )()
