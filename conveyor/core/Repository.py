import typing
import pydantic
import itertools
import dataclasses

from . import Item, ItemQuery, ItemPart, PartRepository



@dataclasses.dataclass(frozen=True, kw_only=False)
class Repository:

	parts: typing.Sequence[PartRepository]

	@pydantic.validator('parts')
	def parts_correct(cls, parts):
		if len(parts) < 1:
			raise ValueError(f'Repository must have at least 1 part ({len(parts)} provided)')
		return parts

	@pydantic.validate_arguments
	def _reserve(self, item_query: ItemQuery) -> None:
		reserver = Item.Reserver(exists=True)
		for p in reversed(self.parts):
			p.reserve(item_query, reserver)

	@pydantic.validate_arguments
	def _unreserve(self, item: Item) -> None:
		for p in reversed(self.parts):
			p.unreserve(item)

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		for p in reversed(self.parts):
			p.add(item)

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery) -> typing.Iterable[Item]:

		self._reserve(item_query)

		result = (ItemPart(),)
		for repository in self.parts:
			result = itertools.chain.from_iterable([
				repository.get(
					item_query,
					item_part
				)
				for item_part in result
			])

		previous: Item | None = None
		for r in result:
			yield r.item
			if previous is not None:
				self._unreserve(previous)
			previous = r.item

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		for p in reversed(self.parts):
			p[old] = new

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		for p in self.parts:
			del p[item]

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:

		result = self.parts[-1].transaction(f)
		for p in reversed(self.parts[:-1]):
			result = p.transaction(result)

		return result