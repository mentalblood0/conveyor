import pydantic

from ..core import Item, Repository



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class TransformerProcessor:

	@pydantic.validate_arguments
	def __call__(self, item: Item) -> Item:
		return item


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Transformer:

	Processor = TransformerProcessor

	repository: Repository
	processor: TransformerProcessor

	@pydantic.validate_arguments
	def __call__(self, item: Item) -> None:
		self.repository[item] = self.processor(item)