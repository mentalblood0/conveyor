import abc
import typing
import dataclasses

from ...Item import Item

from .. import Action
from ..Processor import Processor


@dataclasses.dataclass(frozen=True, kw_only=True)
class Mover(Processor[Item, Action.Action], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def process(
        self, input: Item
    ) -> typing.Iterable[Item.Status | Item.Metadata | Item]:
        """"""

    def actions(self, i: Item, o: Item.Status | Item.Metadata | Item):
        match o:
            case Item.Status():
                yield Action.Update(old=i, new=dataclasses.replace(i, status=o))
            case Item.Metadata():
                yield Action.Update(
                    old=i,
                    new=dataclasses.replace(i, metadata=i.metadata | o.value),
                )
            case Item():
                assert o.chain == i.chain, (
                    f"Output chain ({o.chain}) must be equal "
                    f"to input chain ({i.chain})"
                )
                yield Action.Append(o)

    @typing.final
    def __call__(
        self, input: typing.Callable[[], typing.Iterable[Item]], config: typing.Any = {}
    ) -> typing.Iterable[Action.Action]:
        for i in input():
            try:
                for o in self.process(i):
                    for a in self.actions(i, o):
                        yield a
            except Exception as e:
                raise self.error(i, e)

            yield Action.Success(i)
            break
