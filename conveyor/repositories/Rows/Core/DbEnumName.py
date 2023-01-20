import pydantic

from ....core import Item, Transforms



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class DbEnumName(Transforms.Safe[Item.Metadata.Key, str]):

	postfix: str

	@pydantic.validate_arguments
	def transform(self, i: Item.Metadata.Key) -> str:
		return f'{i.value}_{self.postfix}'

	def __invert__(self) -> 'ItemKey':
		return ItemKey(self.postfix)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class ItemKey(Transforms.Safe[str, Item.Metadata.Key]):

	postfix: str

	@pydantic.validate_arguments
	def transform(self, i: str) -> Item.Metadata.Key:
		return Item.Metadata.Key(i[:-len(self.postfix) - 1])

	def __invert__(self) -> DbEnumName:
		return DbEnumName(self.postfix)