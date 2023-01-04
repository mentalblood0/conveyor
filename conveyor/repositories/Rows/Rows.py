import typing
import pydantic
import contextlib
import dataclasses

from .Core import Core
from ...core import Item, Query, Part, PartRepository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Rows(PartRepository):

	Core = Core

	rows: Core

	@pydantic.validate_arguments
	def append(self, item: Item) -> None:
		return self.rows.append(self.rows.Item.from_item(item))

	@pydantic.validate_arguments
	def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
		for r in self.rows[item_query]:
			yield dataclasses.replace(
				accumulator,
				type_=r.type,
				status_=r.status,
				digest_=r.digest,
				chain_=Item.Chain(ref=r.chain),
				metadata_=r.metadata,
				created_=r.created,
				reserver_=r.reserver
			)

	@pydantic.validate_arguments
	def __setitem__(self, old: Item, new: Item) -> None:
		return self.rows.__setitem__(self.rows.Item.from_item(old), self.rows.Item.from_item(new))

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		return self.rows.__delitem__(self.rows.Item.from_item(item))

	@pydantic.validate_arguments
	@contextlib.contextmanager
	def transaction(self) -> typing.Iterator[typing.Self]:
		with self.rows.transaction() as t:
			yield dataclasses.replace(self, rows = t)

	@pydantic.validate_arguments
	def __contains__(self, item: Item) -> bool:
		return self.rows.Item.from_item(item) in self.rows