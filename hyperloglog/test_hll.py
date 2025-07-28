from .hll import HyperLogLog
import pytest


def test_can_create_hyperloglog():
    hll = HyperLogLog()
    assert hll is not None


def test_estimates_cardinality_of_empty_set():
    hll = HyperLogLog()
    assert hll.cardinality == 0


def test_can_add_item_and_estimate_cardinality():
    hll = HyperLogLog()
    hll.add("foo")
    cardinality = hll.cardinality
    assert cardinality == pytest.approx(1, abs=1)


def test_adding_multiple_items_increases_cardinality():
    hll = HyperLogLog()
    hll.add("foo")
    hll.add("bar")
    cardinality = hll.cardinality
    assert cardinality == pytest.approx(2, abs=1)

    hll.add("baz")
    hll.add("quux")
    hll.add("axe")
    new_cardinality = hll.cardinality
    assert new_cardinality == pytest.approx(5, abs=1)


def test_adding_duplicate_items_doesnt_increase_cardinality():
    hll = HyperLogLog()
    hll.add("foo")
    cardinality = hll.cardinality
    assert cardinality == pytest.approx(1, abs=1)
    for _ in range(1_000):
        hll.add("foo")
    new_cardinality = hll.cardinality
    assert new_cardinality == pytest.approx(1, abs=1)


def test_uses_fixed_memory():
    hll = HyperLogLog()
    for i in range(1_000):
        hll.add(f"item:{i}")
    assert hasattr(hll, "_buckets")


def test_cardinality_large_number_of_items():
    hll = HyperLogLog(precision=10)
    num_items = 100_000
    for i in range(num_items):
        hll.add(f"item:{i}")

    # expected error is approx 1.04 / sqrt(2^precision)
    # for p=10, m=1024, error = 1.04 / 32 = 0.0325
    error_margin = 0.1

    cardinality = hll.cardinality
    assert (
        num_items * (1 - error_margin) <= cardinality <= num_items * (1 + error_margin)
    )


def test_precision_parameter_affects_buckets():
    hll_p4 = HyperLogLog(precision=4)
    assert hll_p4._num_buckets == 16

    hll_p8 = HyperLogLog(precision=8)
    assert hll_p8._num_buckets == 256


def test_accuracy_improves_with_precision():
    num_items = 10_000

    hll_p4 = HyperLogLog(precision=4)  # lower precision
    hll_p12 = HyperLogLog(precision=12)  # higher precision

    for i in range(num_items):
        item = f"item{i}"
        hll_p4.add(item)
        hll_p12.add(item)

    card_p4 = hll_p4.cardinality
    card_p12 = hll_p12.cardinality

    error_p4 = abs(card_p4 - num_items) / num_items
    error_p12 = abs(card_p12 - num_items) / num_items

    assert error_p12 < error_p4


def test_add_bytes():
    hll = HyperLogLog()
    hll.add(b"foo")
    cardinality = hll.cardinality
    assert cardinality == pytest.approx(1, abs=1)
