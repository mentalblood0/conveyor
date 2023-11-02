import pytest
import typing
import dataclasses

from conveyor.core import Worker, Item
from conveyor.core.Worker import processors
from conveyor.core import Mask, Query, Repository

from ..common import *


@pytest.fixture
def mover() -> processors.Mover:
    class M(processors.Mover):
        def process(self, payload: Item) -> typing.Iterable[Item.Status | Item]:
            yield Item.Status(f"{payload.status.value}_")

            n = payload.metadata["n"]
            match n:
                case int():
                    for _ in range(n):
                        yield dataclasses.replace(payload, kind=Item.Kind("new"))
                case _:
                    """"""

    return M()


@pytest.fixture
def worker(
    receiver: Worker.Receiver, mover: processors.Mover, repository: Repository
) -> Worker.Worker:
    return Worker.Worker(receiver=receiver, processor=mover, repository=repository)


def test_mover_change_status_create_one_item(
    worker: Worker.Worker, item: Item, query_all: Query
):
    item = dataclasses.replace(
        item, metadata=item.metadata | {Item.Metadata.Key("n"): 1}
    )
    status = item.status
    worker.repository.append(item)

    for _ in range(2):
        worker()
        assert len(worker.repository) == 2
        for i in worker.repository[query_all]:
            assert i == dataclasses.replace(
                item, status=Item.Status(f"{status.value}_")
            )
        for i in worker.repository[Query(mask=Mask(kind=Item.Kind("new")), limit=None)]:
            assert i == dataclasses.replace(item, kind=Item.Kind("new"))


def test_mover_change_status_create_many_items(
    worker: Worker.Worker, item: Item, query_all: Query
):
    n = 3
    item = dataclasses.replace(
        item, metadata=item.metadata | {Item.Metadata.Key("n"): n}
    )
    status = item.status
    worker.repository.append(item)

    for _ in range(2):
        worker()
        assert len(worker.repository) == 1 + n
        for i in worker.repository[query_all]:
            assert i == dataclasses.replace(
                item, status=Item.Status(f"{status.value}_")
            )
        for i in worker.repository[Query(mask=Mask(kind=Item.Kind("new")), limit=None)]:
            assert i == dataclasses.replace(item, kind=Item.Kind("new"))
