import typing
import pydantic

from ..core import Item, Repository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class SynthesizerProcessor:

	@pydantic.validate_arguments
	def __call__(self, item: Item, source: Item) -> typing.Iterable[Item]:
		return ()



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Synthesizer:

	Processor = SynthesizerProcessor

	repository: Repository
	processor: SynthesizerProcessor
	output_statuses: tuple[Item.Status]

	@pydantic.validate_arguments
	def __call__(self, item: Item, source: Item) -> None:
		for i in self.processor(item, source):
			self.repository.add(i)