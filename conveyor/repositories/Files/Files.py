import typing
import pydantic
import dataclasses

from .Files_ import Files_
from ...core import Item, Query, Part, PartRepository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Files(PartRepository):

	Core = Files_

	files: Core

	@pydantic.validate_arguments
	def add(self, item: Item) -> None:
		return self.files.add(item.data)

	@pydantic.validate_arguments
	def get(self, item_query: Query, accumulator: Part) -> typing.Iterable[Part]:
		data = self.files[accumulator.digest]
		yield dataclasses.replace(
			accumulator,
			data_=data
		)

	@pydantic.validate_arguments
	def __delitem__(self, item: Item) -> None:
		return self.files.__delitem__(item.data.digest)

	@pydantic.validate_arguments
	def transaction(self, f: typing.Callable[[], None]) -> None:
		f()