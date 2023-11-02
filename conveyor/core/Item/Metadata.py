import types
import typing
import datetime
import dataclasses

from .Word import Word
from .Enumerable import Enumerable


@dataclasses.dataclass(frozen=True, kw_only=False)
class Metadata:
    class Key(Word):
        """"""

    Value = str | int | float | datetime.datetime | Enumerable | None

    Mutable = dict[Key, Value]

    Enumerable = Enumerable

    value_: dict[Key, Value] | types.MappingProxyType[Key, Value]

    @property
    def value(self) -> types.MappingProxyType[Key, Value]:
        return types.MappingProxyType(self.value_)

    def __getitem__(self, key: str | Key) -> Value:
        match key:
            case Metadata.Key():
                return self.value[key]
            case str():
                return self[Metadata.Key(key)]

    def __or__(self, o: dict[Key, Value] | typing.Mapping[Key, Value]) -> typing.Self:
        return Metadata(self.value | o)

    def __ror__(self, __value: typing.Any) -> typing.Self:
        return self | __value

    def keys(self):
        return self.value.keys()

    def items(self):
        return self.value.items()

    def __iter__(self):
        return self.value.__iter__()
