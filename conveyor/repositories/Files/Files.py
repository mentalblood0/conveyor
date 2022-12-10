import typing
import pydantic
import dataclasses

from ._Files import _Files
from ...core import Item, ItemQuery, ItemPart, Chain, PartRepository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Files(PartRepository):

	files: _Files

	@pydantic.validate_arguments
	def reserve(self, item_query: ItemQuery, reserver: Item.Reserved):
		pass

	@pydantic.validate_arguments
	def unreserve(self, item: Item) -> None:
		pass

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		return self.files.add(item.data)

	@pydantic.validate_arguments
	def get(self, item_query: ItemQuery, accumulator: ItemPart) -> typing.Iterable[ItemPart]:
		data = self.files[accumulator.digest]
		yield dataclasses.replace(
			accumulator,
			data_=data,
			chain_=Chain(ref=data)
		)

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		pass

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		return self.files.__delitem__(item.data.digest)

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:
		return f