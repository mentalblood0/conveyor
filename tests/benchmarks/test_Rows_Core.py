from tests.common import *



@pytest.mark.benchmark(group='rows')
def test_add_same(benchmark, rows: Rows.Core, row: Rows.Core.Item):
	benchmark(rows.append, row)
	rows.clear()


@pytest.mark.benchmark(group='rows')
def test_get_same_one(benchmark, rows: Rows.Core, row: Rows.Core.Item, query_all: Query):
	rows.append(row)
	benchmark(lambda: rows.__getitem__(query_all).__iter__().__next__())
	rows.clear()