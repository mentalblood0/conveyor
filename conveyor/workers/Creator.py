import typing
import pydantic

from ..core import Item, Repository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class CreatorProcessor:

	@pydantic.validate_arguments
	def __call__(self, source: object) -> typing.Iterable[Item]:
		return ()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Creator:

	Processor = CreatorProcessor

	repository: Repository
	processor: CreatorProcessor

	@pydantic.validate_arguments
	def __call__(self, source: object) -> None:
		for i in self.processor(source):
			self.repository.add(i)