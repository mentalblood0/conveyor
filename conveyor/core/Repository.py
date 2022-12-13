import typing
import pydantic
import functools
import dataclasses

from . import Item, ItemQuery, ItemPart, PartRepository



Parts = typing.Sequence[PartRepository]


@dataclasses.dataclass(frozen=True, kw_only=False)
class Repository:

	Parts = Parts

	parts: Parts

	@pydantic.validator('parts')
	def parts_correct(cls, parts: Parts) -> Parts:
		if len(parts) < 1:
			raise ValueError(f'Repository must have at least 1 part ({len(parts)} provided)')
		return parts

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		for p in reversed(self.parts):
			p.add(item)

	@pydantic.validate_arguments
	def _get(self, query: ItemQuery, repositories: typing.Sequence[PartRepository], parts: typing.Iterable[ItemPart] = (ItemPart(),)) -> typing.Iterable[Item]:

		if not len(repositories):
			for p in parts:
				yield p.item

		for p in parts:
			for item in self._get(
				query=query,
				repositories=repositories[1:],
				parts=repositories[0].get(query, p)
			):
				yield item

	@pydantic.validate_arguments
	def _reserve(self, item_query: ItemQuery, reserver: Item.Reserver) -> None:

		reserved = 0

		while True:

			reserved_before = reserved

			for i in self.__getitem__(
				item_query=dataclasses.replace(
					item_query,
					mask=dataclasses.replace(
						item_query.mask,
						reserver=Item.Reserver(exists=False)
					)
				),
				for_reserve=True
			):

				try:
					self[i] = dataclasses.replace(i, reserver=reserver)
				except KeyError:
					continue

				if reserved == item_query.limit:
					return

			if reserved == reserved_before:
				return

	@pydantic.validate_arguments
	def __getitem__(self, item_query: ItemQuery, for_reserve=False) -> typing.Iterable[Item]:

		if not for_reserve:

			reserver = Item.Reserver(exists=True)
			self._reserve(item_query, reserver)

			item_query = dataclasses.replace(
				item_query,
				mask=dataclasses.replace(
					item_query.mask,
					reserver=reserver
				)
			)

		return self._get(
			query=item_query,
			repositories=self.parts
		)

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item, for_reserve=False) -> None:
		new = dataclasses.replace(new, reserver=Item.Reserver(exists=False)) if for_reserve else new
		for p in reversed(self.parts):
			p[old] = new

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		for p in self.parts:
			try:
				del p[item]
			except KeyError:
				break

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable) -> typing.Callable:
		return functools.reduce(lambda result, t: t.transaction(result), reversed(self.parts), f)