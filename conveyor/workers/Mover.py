import typing
import pydantic

from ..core import Item, Repository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class MoverProcessor:

	@pydantic.validate_arguments
	def __call__(self, item: Item) -> tuple[Item, typing.Iterable[Item]]:
		return (item, ())


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Mover:

	Processor = MoverProcessor

	repository: Repository
	processor: MoverProcessor
	output_statuses: tuple[Item.Status]

	@pydantic.validate_arguments
	def __call__(self, item: Item) -> None:

		transformed, created = self.processor(item)

		self.repository[item] = transformed
		for c in created:
			self.repository.add(c)