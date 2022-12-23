import pydantic

from ..core import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class SynthesizerProcessor:

	@pydantic.validate_arguments
	def __call__(self, item: Item, source: Item) -> tuple[Item]:
		return tuple()



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Synthesizer:

	Processor = SynthesizerProcessor

	processor: Processor