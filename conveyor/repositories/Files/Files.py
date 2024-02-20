import contextlib
import dataclasses
import typing

from ...core import Item, Part, PartRepository, Query
from .Core.Core import Core


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

    def __len__(self) -> int:
        return len(self.files)

    def clear(self) -> None:
        self.files.clear()
