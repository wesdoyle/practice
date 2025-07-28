from .hll import HyperLogLog
import pytest

def test_can_create_hyperloglog():
    hll = HyperLogLog()
    assert hll is not None


def test_estimates_cardinality_of_empty_set():
    hll = HyperLogLog()
    assert hll.cardinality() == 0

def test_can_add_item_and_estimate_cardinality():
    hll = HyperLogLog()
    hll.add("foo")
    cardinality = hll.cardinality()
    assert cardinality == pytest.approx(0.5, 1)

def test_adding_multiple_items_increases_cardinality():
    hll = HyperLogLog()
    hll.add("foo")
    hll.add("bar")
    cardinality = hll.cardinality()
    assert cardinality == pytest.approx(3, abs=1)

    hll.add("baz")
    hll.add("quux")
    hll.add("axe")
    new_cardinality = hll.cardinality()
    assert new_cardinality == pytest.approx(5, abs=1)

def test_adding_duplicate_items_doesnt_increase_cardinality():
    hll = HyperLogLog()
    hll.add("foo")
    cardinality = hll.cardinality()
    assert cardinality == pytest.approx(1, abs=1)
    for i in range(1_000):
        hll.add("foo")
    assert cardinality == pytest.approx(1, abs=1)
