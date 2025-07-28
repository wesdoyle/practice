from .count_min_sketch import CountMinSketch

def test_can_create_count_min_sketch():
    cms = CountMinSketch()
    assert cms is not None
