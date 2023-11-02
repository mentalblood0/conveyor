import abc
import typing
import dataclasses

from ...Item import Item

from .. import Action
from ..Processor import Processor


@dataclasses.dataclass(frozen=True, kw_only=True)
class Synthesizer(Processor[Item, Action.Action], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def process(
        self, payload: Item, matched: typing.Iterable[Item]
    ) -> typing.Iterable[Item.Status | Item]:
        """"""

    def _actions(self, i: Item, o: Item.Status | Item):
        match o:
            case Item.Status():
                yield Action.Update(old=i, new=dataclasses.replace(i, status=o))
            case Item():
                if o.chain != i.chain:
                    raise ValueError(
                        f"Output chain ({o.chain}) must be equal "
                        f"to input chain ({i.chain})"
                    )
                yield Action.Append(o)

    def _process(
        self, items: typing.Iterator[Item], i: Item
    ) -> typing.Generator[
        Action.Update | Action.Append | Action.Success, typing.Any, None
    ]:
        try:
            for o in self.process(i, iter(items)):
                yield from self._actions(i, o)
        except Exception as e:
            raise self.error(i, e) from e

        yield Action.Success(i)

    @typing.final
    def __call__(
        self,
        payload: typing.Callable[[], typing.Iterable[Item]],
        config: typing.Any = None,
    ) -> typing.Iterable[Action.Action]:
        for i in (iterator := iter(payload())):
            yield from self._process(iterator, i)
            break
