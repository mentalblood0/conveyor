import typing
import pydantic
import contextlib
import dataclasses

from ..Item.Part import Part
from .Query import Query
from ..Item.Item import Item
from .PartRepository import PartRepository



Parts = typing.Sequence[PartRepository]


@dataclasses.dataclass(frozen=True, kw_only=False)
class Repository:

	Parts = Parts

	parts        : Parts
	transaction_ : bool = False

	@pydantic.validator('parts')
	def parts_valid(cls, parts: Parts) -> Parts:
		match len(parts):
			case 0:
				raise pydantic.ListMinLengthError(limit_value = 1)
			case _:
				return parts

	@pydantic.validate_arguments
	def _unreserved(self, item: Item) -> Item:
		return dataclasses.replace(item, reserver = Item.Reserver(exists = False))

	@pydantic.validate_arguments
	def append(self, item: Item) -> None:
		for p in reversed(self.parts):
			p.append(self._unreserved(item))

	@pydantic.validate_arguments
	def _get(self, query: Query, repositories: typing.Sequence[PartRepository], parts: typing.Iterable[Part] = (Part(),)) -> typing.Iterable[Item]:
		match len(repositories):
			case 0:
				for p in parts:
					yield p.item
			case _:
				for p in parts:
					for item in self._get(
						query        = query,
						repositories = repositories[1:],
						parts        = repositories[0].get(query, p)
					):
						yield item

	@pydantic.validate_arguments
	def __getitem__(self, item_query: Query) -> typing.Iterable[Item]:

		reserver = Item.Reserver(exists = True)
		got: int = 0

		for i in self._get(
			query = dataclasses.replace(
				item_query,
				mask = dataclasses.replace(
					item_query.mask,
					reserver = Item.Reserver(exists = False)
				)
			),
			repositories = self.parts
		):

			reserved = dataclasses.replace(i, reserver = reserver)
			try:
				self.__setitem__(i, reserved, True)
			except KeyError:
				continue

			yield reserved
			got += 1
			if got == item_query.limit:
				break

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item, for_reserve: bool = False) -> None:

		if for_reserve:
			_new = new
		else:
			_new = self._unreserved(new)

		with self.transaction() as t:
			for p in reversed(t.parts):
				try:
					p[old] = _new
				except NotImplementedError:
					pass

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		with self.transaction() as t:
			for p in t.parts:
				try:
					del p[item]
				except KeyError:
					break

	@pydantic.validate_arguments
	@contextlib.contextmanager
	def _transaction(self, parts_to_include: typing.Sequence[PartRepository]) -> typing.Iterator[typing.Sequence[PartRepository]]:
		match len(parts_to_include):
			case 0:
				yield ()
			case _:
				with parts_to_include[0].transaction() as t:
					with self._transaction(parts_to_include[1:]) as _t:
						yield (t, *_t)

	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:
		match self.transaction_:
			case True:
				yield self
			case False:
				with self._transaction(self.parts) as transaction_parts:
					yield dataclasses.replace(
						self,
						parts        = transaction_parts,
						transaction_ = True
					)

	@pydantic.validate_arguments
	def __contains__(self, item: Item) -> bool:
		return all(item in p for p in self.parts)

	def __len__(self) -> pydantic.NonNegativeInt:
		return max(len(p) for p in self.parts)

	def clear(self) -> None:
		with self.transaction() as t:
			for p in t.parts:
				p.clear()