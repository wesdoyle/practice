from .count_min_sketch import CountMinSketch

def test_can_create_count_min_sketch():
    cms = CountMinSketch()
    assert cms is not None

def test_frequency_of_unseen_item_is_zero():
    cms = CountMinSketch()
    assert cms.frequency("foo") == 0
    assert cms.frequency("bar") == 0
