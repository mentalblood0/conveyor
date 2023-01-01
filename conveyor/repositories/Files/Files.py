import typing
import pydantic
import dataclasses

from .Core import Core
from ...core import Item, Query, Part, PartRepository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Files(PartRepository):

	Core = Core

	files: Core

	@pydantic.validate_arguments
	def append(self, item: Item) -> None:
		return self.files.append(item.data)

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