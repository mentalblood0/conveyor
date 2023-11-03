import typing
import datetime
import traceback
import dataclasses

from ... import Item, Repository

from .. import Action
from ..Processor import Processor


@dataclasses.dataclass(frozen=True, kw_only=True)
class Error(Action.Action):
    old: Item
    exception: Exception

    kind: Item.Kind

    @property
    def item(self) -> Item:
        return Item(
            kind=self.kind,
            status=Item.Status("created"),
            data=Item.Data(
                value="\n".join(traceback.format_exception(self.exception)).encode()
            ),
            metadata=Item.Metadata(
                {
                    Item.Metadata.Key("error_type"): Item.Metadata.Enumerable(
                        self.exception.__class__.__name__
                    ),
                    Item.Metadata.Key("error_text"): str(self.exception),
                    Item.Metadata.Key("item_type"): self.old.kind,
                    Item.Metadata.Key("item_status"): self.old.status.value,
                }
            ),
            chain=Item.Chain(ref=Item.Data(value=b"")),
            reserver=Item.Reserver(None),
            created=Item.Created(datetime.datetime.now()),
        )

    def __call__(self, repository: Repository) -> None:
        Action.Append(self.item)(repository)

    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
        yield ("old", self.old)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Solution(Action.Action):
    ref: Item | Action.Success

    kind: Item.Kind

    @property
    def old(self) -> Item:
        match self.ref:
            case Item():
                return self.ref
            case Action.Success():
                return self.ref.item

    def __call__(self, repository: Repository) -> None:
        Action.Delete(Error(old=self.old, exception=Exception(), kind=self.kind).item)(
            repository
        )

    @property
    def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
        yield ("old", self.old)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Logger(Processor[Action.Action, Action.Action]):
    Error = Error
    Solution = Solution

    normal: Item.Kind
    errors: Item.Kind

    def process_success(self, a: Action.Success):
        yield Solution(ref=a, kind=self.errors)

    def info(self, a: Action.Action):
        result = Item.Metadata({})
        for k, v in a.info:
            match v:
                case Item.Metadata.Value:
                    result = result | {Item.Metadata.Key(f"action_{k}"): v}
                case Item():
                    result = result | {
                        Item.Metadata.Key(f"action_{k}_type"): v.kind.value
                    }
                    result = result | {
                        Item.Metadata.Key(f"action_{k}_status"): v.status.value
                    }
                case _:
                    """"""
        return result

    def entry(self, a: Action.Action):
        return Item(
            kind=self.normal,
            status=Item.Status("preaction"),
            data=Item.Data(value=b""),
            metadata=self.info(a)
            | {
                Item.Metadata.Key("action"): Item.Metadata.Enumerable(
                    a.__class__.__name__
                ),
            },
            chain=Item.Chain(ref=Item.Data(value=str(a).encode())),
            reserver=Item.Reserver(None),
            created=Item.Created(datetime.datetime.now()),
        )

    def process_other(self, a: Action.Action):
        entry = self.entry(a)
        yield Action.Append(entry)
        yield a
        yield Action.Update(
            old=entry,
            new=dataclasses.replace(entry, status=Item.Status("postaction")),
        )

    def __call__(
        self,
        payload: typing.Callable[[], typing.Iterable[Action.Action]],
        _: typing.Any,
    ) -> typing.Iterable[Action.Action]:
        try:
            for a in payload():
                if isinstance(a, Action.Success):
                    return self.process_success(a)
                return self.process_other(a)
        except Exception as e:
            if isinstance(e, Processor.Error):
                _e: Processor.Error[Item] = e
                yield Error(old=_e.payload, exception=_e.exception, kind=self.errors)
            else:
                raise
