import abc
import typing
import dataclasses

from ...Item import Item

from .. import Action
from ..Processor import Processor


@dataclasses.dataclass(frozen=True, kw_only=True)
class Mover(Processor[Item, Action.Action], abc.ABC):
    @abc.abstractmethod
    def process(
        self, payload: Item
    ) -> typing.Iterable[Item.Status | Item.Metadata | Item]:
        """"""

    def _actions(self, i: Item, o: Item.Status | Item.Metadata | Item):
        match o:
            case Item.Status():
                yield Action.Update(old=i, new=dataclasses.replace(i, status=o))
            case Item.Metadata():
                yield Action.Update(
                    old=i,
                    new=dataclasses.replace(i, metadata=i.metadata | o.value),
                )
            case Item():
                if o.chain != i.chain:
                    raise ValueError(
                        f"Output chain ({o.chain}) must be equal "
                        f"to input chain ({i.chain})"
                    )
                yield Action.Append(o)

    @typing.final
    def __call__(
        self,
        payload: typing.Callable[[], typing.Iterable[Item]],
        config: typing.Any = None,
    ) -> typing.Iterable[Action.Action]:
        for i in payload():
            try:
                for o in self.process(i):
                    yield from self._actions(i, o)
            except Exception as e:
                raise self.error(i, e) from e

            yield Action.Success(i)
            break
