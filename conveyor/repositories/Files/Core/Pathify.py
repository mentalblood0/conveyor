import typing
import pathlib
import dataclasses

from ....core.Item import Digest

from ....core.Transforms import Transform, Safe


@dataclasses.dataclass(frozen=True, kw_only=False)
class Segment(Safe[Digest, typing.Sequence[str]]):
    def _segment(self, s: str) -> str:
        return {"+": "plus", "/": "slash", "=": "equal"}.get(s, s)

    def transform(self, i: Digest) -> typing.Sequence[str]:
        return [*map(self._segment, i.string)]

    def __invert__(self) -> "Desegment":
        return Desegment()


@dataclasses.dataclass(frozen=True, kw_only=False)
class Desegment(Safe[typing.Sequence[str], Digest]):
    def _desegment(self, s: str) -> str:
        return {"plus": "+", "slash": "/", "equal": "="}.get(s, s)

    def transform(self, i: typing.Sequence[str]) -> Digest:
        return Digest.from_base64("".join(self._desegment(s) for s in i))


Granulation = typing.Callable[[int], int]


@dataclasses.dataclass(frozen=True, kw_only=False)
class Group(Safe[typing.Sequence[str], pathlib.Path]):
    granulation: Granulation

    def _group(
        self, line: typing.Iterable[str], size: typing.Callable[[int], int]
    ) -> typing.Iterable[str]:
        buffer = ""
        n = 0

        for e in line:
            if len(e) == 1:
                buffer += e
                if len(buffer) == size(n):
                    yield buffer
                    n += 1
                    buffer = ""
            else:
                yield buffer
                n += 1
                buffer = ""
                yield e
                n += 1

    def transform(self, i: typing.Sequence[str]) -> pathlib.Path:
        return pathlib.Path(*self._group(i, self.granulation))

    def __invert__(self) -> "Ungroup":
        return Ungroup(inverted_granulation=self.granulation)


@dataclasses.dataclass(frozen=True, kw_only=False)
class Ungroup(Safe[pathlib.Path, typing.Sequence[str]]):
    inverted_granulation: Granulation = lambda n: 2

    def transform(self, i: pathlib.Path) -> typing.Sequence[str]:
        result: list[str] = []

        for p in i.parts:
            if p in ("plus", "slash", "equal"):
                result.append(p)
            else:
                result.extend(p)

        return result


class Pathify:
    def __new__(
        cls, granulation: typing.Callable[[int], int]
    ) -> Transform[Digest, pathlib.Path]:
        return Segment() + Group(granulation)
