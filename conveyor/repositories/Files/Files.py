import typing
import contextlib
import dataclasses

from .Core.Core import Core
from ...core import Item, Query, Part, PartRepository


@dataclasses.dataclass(frozen=True, kw_only=False)
class Files(PartRepository):
    Core = Core

    files: Core

    def append(self, item: Item) -> None:
        return self.files.append(item.data)

    def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
        data = self.files[accumulator.digest]
        yield dataclasses.replace(accumulator, data_=data)

    def __delitem__(self, item: Item) -> None:
        del self.files[item.data.digest]

    @contextlib.contextmanager
    def transaction(self) -> typing.Iterator[typing.Self]:
        with self.files.transaction() as t:
            yield dataclasses.replace(self, files=t)

    def __contains__(self, item: Item) -> bool:
        return item.data.digest in self.files

    def __len__(self) -> int:
        return len(self.files)

    def clear(self) -> None:
        self.files.clear()
