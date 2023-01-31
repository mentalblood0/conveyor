import uuid
import base64
import typing
import pydantic



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Reserver:

	exists : bool
	value  : str | None = None

	@pydantic.validator('value')
	def value_valid(cls, value: str | None, values: dict[str, bool]) -> str | None:
		if values['exists']:
			match value:
				case str():
					return value
				case None:
					return base64.b64encode(uuid.uuid4().bytes).decode('ascii')
				case _ as unreachable:
					typing.assert_never(unreachable)
		else:
			return None