import pydantic

from ..core import Item



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Creator:

	def __call__(self, *args, **kwargs) -> tuple[Item]:
		return tuple()