import typing
import pydantic

from . import Files
from ...core import Digest, Data, Item, ItemQuery


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class ItemsFiles:

	files: Files

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
	def __getitem__(self, digest: Digest) -> Data:
		return self.files[digest]

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		pass

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		return self.files.__delitem__(item.data.digest)

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:
		return f