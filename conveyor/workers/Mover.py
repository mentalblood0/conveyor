import pydantic

from ..core import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Mover:

	@pydantic.validate_arguments
	def __call__(self, item: Item) -> tuple[Item, tuple[Item]]:
		return (item, tuple())