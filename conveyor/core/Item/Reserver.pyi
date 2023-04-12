class Reserver:
    exists: bool
    value: str | None
    def value_valid(cls, value: str | None, values: dict[str, bool]) -> str | None: ...
