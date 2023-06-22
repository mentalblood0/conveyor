import pydantic

from ....core import Item, Transforms



@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class DbTableName(Transforms.Safe[Item.Type, str]):

	prefix: str

	@pydantic.validate_arguments
	def transform(self, i: Item.Type) -> str:
		return f'{self.prefix}_{i.value}'

	def __invert__(self) -> 'ItemType':
		return ItemType(self.prefix)


@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class ItemType(Transforms.Safe[str, Item.Type]):

	prefix: str

	@pydantic.validate_arguments
	def transform(self, i: str) -> Item.Type:
		return Item.Type(i[len(self.prefix) + 1:])

	def __invert__(self) -> DbTableName:
		return DbTableName(self.prefix)
