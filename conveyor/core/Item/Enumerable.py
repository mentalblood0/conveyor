import pydantic



@pydantic.dataclasses.dataclass(frozen = True, kw_only = False)
class Enumerable:
	value: pydantic.StrictStr | None