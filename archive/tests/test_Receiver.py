import pytest

from conveyor.common import ItemId
from conveyor.core import Item, Receiver
from conveyor.core.Receiver import composeReceiverId

from .common import *



type = 'undefined'
status = 'created'


@pytest.fixture
def item():
	return Item(
		type=type,
		status=status,
		data='lalala',
		metadata={
			'message_id': 'lololo'
		}
	)


@pytest.fixture
def receiver():
	result = Receiver(repository=repository)
	result.input_type = type
	result.input_status = status
	return result


@pytest.fixture(autouse=True)
def clearDb():
	repository._drop(type)


def test_reserve(receiver, item):
	repository.create(item)
	assert receiver.reserve() == 1
	assert receiver.reserve() == 0


def test_unreserve(receiver, item):
	repository.create(item)
	result = repository.get(item.type)[0]
	assert receiver.reserve() == 1
	assert receiver.unreserve([ItemId(result.id)]) == 1


def test_receiveItems_one(receiver, item):

	repository.create(item)

	item = repository.get(type)[0]
	assert receiver.receiveItems() == [item]


def test_receiveItems_many(receiver, item):

	for i in range(3):
		repository.create(item)

	items = repository.get(type, limit=None)
	assert receiver.receiveItems() == items


def test_receiveItems_repeat(receiver, item):

	repository.create(item)

	item = repository.get(type)[0]
	first = receiver.receiveItems()
	second = receiver.receiveItems()
	assert first == second


def test_id():

	n = 10**3

	m = set(composeReceiverId() for i in range(n))

	assert n == len(set(m))
	assert all(len(id) <= 31 for id in m)