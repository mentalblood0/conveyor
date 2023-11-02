import typing
import contextlib
import dataclasses

from .Core.Core import Core
from ...core import Item, Query, Part, PartRepository


@dataclasses.dataclass(frozen=True, kw_only=False)
class Rows(PartRepository):
    Core = Core

    rows: Core

    def append(self, item: Item) -> None:
        return self.rows.append(self.rows.Item.from_item(item))

    def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
        for r in self.rows[item_query]:
            yield dataclasses.replace(
                accumulator,
                kind_=r.kind,
                status_=r.status,
                digest_=r.digest,
                chain_=Item.Chain(ref=r.chain),
                metadata_=r.metadata,
                created_=r.created,
                reserver_=r.reserver,
            )

    def __setitem__(self, old: Item, new: Item) -> None:
        self.rows[self.rows.Item.from_item(old)] = self.rows.Item.from_item(new)

    def __delitem__(self, item: Item) -> None:
        del self.rows[self.rows.Item.from_item(item)]

    @contextlib.contextmanager
    def transaction(self) -> typing.Iterator[typing.Self]:
        with self.rows.transaction() as t:
            yield dataclasses.replace(self, rows=t)

    def __contains__(self, item: Item) -> bool:
        return self.rows.Item.from_item(item) in self.rows

    def __len__(self) -> int:
        return len(self.rows)

    def clear(self) -> None:
        return self.rows.clear()
