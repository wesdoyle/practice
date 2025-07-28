from .hll import HyperLogLog

def test_can_create_hyperloglog():
    hll = HyperLogLog()
    assert hll is not None


def test_estimates_cardinality_of_empty_set():
    hll = HyperLogLog()
    assert hll.cardinality() == 0
