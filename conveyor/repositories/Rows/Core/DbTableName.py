import dataclasses

from ....core import Item, Transforms


@dataclasses.dataclass(frozen=True, kw_only=False)
class DbTableName(Transforms.Safe[Item.Kind, str]):
    prefix: str

    def transform(self, i: Item.Kind) -> str:
        return f"{self.prefix}_{i.value}"

    def __invert__(self) -> "ItemType":
        return ItemType(self.prefix)


@dataclasses.dataclass(frozen=True, kw_only=False)
class ItemType(Transforms.Safe[str, Item.Kind]):
    prefix: str

    def transform(self, i: str) -> Item.Kind:
        return Item.Kind(i[len(self.prefix) + 1 :])

    def __invert__(self) -> DbTableName:
        return DbTableName(self.prefix)
