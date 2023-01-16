import dataclasses
from tests.common import *



@pytest.mark.benchmark(group='rows')
def test_add_same(benchmark, rows: Rows.Core, row: Rows.Core.Item):
	benchmark(rows.append, row)
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_get_same_first(benchmark, rows: Rows.Core, row: Rows.Core.Item, query_all: Query):
	rows.append(row)
	benchmark(lambda: rows.__getitem__(query_all).__iter__().__next__())
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_get_same_next(benchmark, rows: Rows.Core, row: Rows.Core.Item, query_all: Query):

	limit = 1000
	query_limited = dataclasses.replace(query_all, limit = limit)
	for _ in range(limit):
		rows.append(row)

	iterator = rows.__getitem__(query_limited).__iter__()
	iterator.__next__()

	benchmark.pedantic(lambda: iterator.__next__(), rounds = limit - 1)

	rows.clear()