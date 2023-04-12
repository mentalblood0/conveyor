import typing
from ..Item import Item as Item
from ..Repository.Query import Query as Query
from ..Repository.Repository import Repository as Repository
from _typeshed import Incomplete

class Receiver:
    MasksElement: Incomplete
    Masks: Incomplete
    masks: Masks
    limit: Query.Limit
    def sequence(self, repository: Repository, first: Item, masks: Masks) -> typing.Iterable[Item]: ...
    def __call__(self, repository: Repository) -> typing.Iterable[typing.Iterable[Item]]: ...
