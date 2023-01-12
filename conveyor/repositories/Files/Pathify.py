import typing
import pathlib
import pydantic

from ...core.Item import Digest

from .Transforms import Transform



@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Segment(Transform[Digest, typing.Sequence[str]]):

	@pydantic.validate_arguments
	def _segment(self, s: str) -> str:
		match s:
			case '+':
				return 'plus'
			case '/':
				return 'slash'
			case '=':
				return 'equal'
			case _:
				return s

	@pydantic.validate_arguments
	def transform(self, i: Digest) -> typing.Sequence[str]:
		return [*map(self._segment, i.string)]

	def __invert__(self) -> 'Desegment':
		return Desegment()


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Desegment(Transform[typing.Sequence[str], Digest]):

	@pydantic.validate_arguments
	def _desegment(self, s: str) -> str:
		match s:
			case 'plus':
				return '+'
			case 'slash':
				return '/'
			case 'equal':
				return '='
			case _:
				return s

	@pydantic.validate_arguments
	def transform(self, i: typing.Sequence[str]) -> Digest:
		return Digest(
			Digest.Base64String(
				''.join(
					self._desegment(s)
					for s in i
				)
			)
		)

	def __invert__(self) -> Segment:
		return Segment()


Granulation = typing.Callable[[pydantic.NonNegativeInt], pydantic.PositiveInt]


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Group(Transform[typing.Sequence[str], pathlib.Path]):

	granulation: Granulation

	@pydantic.validate_arguments
	def _group(self, l: typing.Iterable[str], size: typing.Callable[[int], int]) -> typing.Iterable[str]:

		buffer = ''
		n = 0

		for e in l:
			if len(e) == 1:
				buffer += e
				if len(buffer) == size(n):
					yield buffer
					n += 1
					buffer = ''
			else:
				yield buffer
				n += 1
				buffer = ''
				yield e
				n += 1

	@pydantic.validate_arguments
	def transform(self, i: typing.Sequence[str]) -> pathlib.Path:
		return pathlib.Path(
			*self._group(
				i,
				self.granulation
			)
		)

	def __invert__(self) -> 'Ungroup':
		return Ungroup(inverted_granulation = self.granulation)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Ungroup(Transform[pathlib.Path, typing.Sequence[str]]):

	inverted_granulation: Granulation = lambda n: 2

	@pydantic.validate_arguments
	def transform(self, i: pathlib.Path) -> typing.Sequence[str]:

		result: list[str] = []

		for p in i.parts:
			if p in ('plus', 'slash', 'equal'):
				result.append(p)
			else:
				result.extend(p)

		return result

	def __invert__(self) -> Group:
		return Group(self.inverted_granulation)


class Pathify:
	def __new__(cls, granulation: typing.Callable[[pydantic.NonNegativeInt], pydantic.PositiveInt]) -> Transform[Digest, pathlib.Path]:
		return Segment() + Group(granulation)