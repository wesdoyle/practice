from .count_min_sketch import CountMinSketch

def test_can_create_count_min_sketch():
    cms = CountMinSketch()
    assert cms is not None

def test_frequency_of_unseen_item_is_zero():
    cms = CountMinSketch()
    assert cms.frequency("foo") == 0
    assert cms.frequency("bar") == 0

def test_add_items_and_get_frequency():
    cms = CountMinSketch()
    cms.add("foo")
    assert cms.frequency("foo") == 1
    assert cms.frequency("bar") == 0

def test_multiple_additions_increase_frequency():
    cms = CountMinSketch()
    for i in range(10):
        cms.add("foo")
        assert cms.frequency("foo") == i + 1

    cms.add("bar")
    assert cms.frequency("bar") == 1
    assert cms.frequency("foo") == 10

def test_can_create_with_width_and_depth_params():
    cms = CountMinSketch(width=1_000, depth = 4)
    cms.add("test")
    assert cms.frequency("test") == 1
