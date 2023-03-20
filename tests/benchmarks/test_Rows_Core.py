import dataclasses
import pytest_benchmark.plugin

from tests.common import *



@pytest.mark.benchmark(group='rows')
def test_append_same(benchmark: pytest_benchmark.plugin.BenchmarkFixture, rows: Rows.Core, row: Rows.Core.Item):
	benchmark(rows.append, row)
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_append_delete(benchmark: pytest_benchmark.plugin.BenchmarkFixture, rows: Rows.Core, row: Rows.Core.Item):

	def f():
		rows.append(row)
		del rows[row]

	benchmark(f)
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_get_same_first(benchmark: pytest_benchmark.plugin.BenchmarkFixture, rows: Rows.Core, row: Rows.Core.Item, query_all: Query):
	rows.append(row)
	benchmark(lambda: next(iter(rows[query_all])))
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_get_same_next(benchmark: pytest_benchmark.plugin.BenchmarkFixture, rows: Rows.Core, row: Rows.Core.Item, query_all: Query):

	limit = 1000
	query_limited = dataclasses.replace(query_all, limit = limit)
	for _ in range(limit):
		rows.append(row)

	iterator = iter(rows[query_limited])
	next(iterator)

	benchmark.pedantic(lambda: next(iterator), rounds = limit - 1)

	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_set_same(benchmark: pytest_benchmark.plugin.BenchmarkFixture, rows: Rows.Core, row: Rows.Core.Item):
	rows.append(row)
	def f():
		rows[row] = row
	benchmark(f)
	rows.clear()


def small_change(variants: typing.Sequence[Rows.Core.Item]) -> typing.Callable[[], Rows.Core.Item]:

	i = -1

	def f():
		nonlocal i
		i += 1
		return variants[i % len(variants)]

	return f


@pytest.mark.benchmark(group='rows')
def test_set_small_change(benchmark: pytest_benchmark.plugin.BenchmarkFixture, rows: Rows.Core, row: Rows.Core.Item):

	initial = dataclasses.replace(row, metadata = Item.Metadata(row.metadata.value | {Item.Metadata.Key('i'): 1}))
	new     = dataclasses.replace(row, metadata = Item.Metadata(row.metadata.value | {Item.Metadata.Key('i'): 2}))

	rows.append(initial)

	generator = small_change([initial, new])

	def f():
		rows[generator()] = generator()
	benchmark(f)
	rows.clear()