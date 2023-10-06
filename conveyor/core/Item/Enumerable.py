import dataclasses



@dataclasses.dataclass(frozen = True, kw_only = False)
class Enumerable:
	value: str | None