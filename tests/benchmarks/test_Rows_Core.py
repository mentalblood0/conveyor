import pytest

from tests.common import *



@pytest.mark.benchmark(group='rows')
def test_add_same(benchmark, rows: Rows.Core, row: Rows.Core.Item):
	benchmark(rows.append, row)
	rows.clear()