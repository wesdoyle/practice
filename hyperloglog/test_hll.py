from .hll import HyperLogLog

def test_can_create_hyperloglog():
    hll = HyperLogLog()
    assert hll is not None
