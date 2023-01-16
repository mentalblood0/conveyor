import dataclasses
from tests.common import *



@pytest.mark.benchmark(group='rows')
def test_add_same(benchmark, rows: Rows.Core, row: Rows.Core.Item):
	benchmark(rows.append, row)
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_get_same_first(benchmark, rows: Rows.Core, row: Rows.Core.Item, query_all: Query):
	rows.append(row)
	benchmark(lambda: rows[query_all].__iter__().__next__())
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_get_same_next(benchmark, rows: Rows.Core, row: Rows.Core.Item, query_all: Query):

	limit = 1000
	query_limited = dataclasses.replace(query_all, limit = limit)
	for _ in range(limit):
		rows.append(row)

	iterator = rows[query_limited].__iter__()
	iterator.__next__()

	benchmark.pedantic(lambda: iterator.__next__(), rounds = limit - 1)

	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_set_same(benchmark, rows: Rows.Core, row: Rows.Core.Item):
	rows.append(row)
	benchmark(lambda: rows.__setitem__(row, row))
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_set_small_change(benchmark, rows: Rows.Core, row: Rows.Core.Item):

	initial = dataclasses.replace(row, metadata = Item.Metadata(row.metadata.value | {Item.Metadata.Key('i'): 1}))
	new     = dataclasses.replace(row, metadata = Item.Metadata(row.metadata.value | {Item.Metadata.Key('i'): 2}))

	rows.append(initial)

	benchmark(lambda: rows.__setitem__(initial, new))
	rows.clear()