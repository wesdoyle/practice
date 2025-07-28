import pytest
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
    cms = CountMinSketch(width=1_000, depth=4)
    cms.add("test")
    assert cms.frequency("test") == 1

def test_init_with_invalid_params_raises_error():
    """Test that creating a CMS with invalid width or depth raises ValueError."""
    with pytest.raises(ValueError, match="width must be a positive integer"):
        CountMinSketch(width=0, depth=5)
    with pytest.raises(ValueError, match="width must be a positive integer"):
        CountMinSketch(width=-1, depth=5)
    with pytest.raises(ValueError, match="width must be a positive integer"):
        CountMinSketch(width=10.5, depth=5)
    
    with pytest.raises(ValueError, match="depth must be a positive integer"):
        CountMinSketch(width=100, depth=0)
    with pytest.raises(ValueError, match="depth must be a positive integer"):
        CountMinSketch(width=100, depth=-1)
    with pytest.raises(ValueError, match="depth must be a positive integer"):
        CountMinSketch(width=100, depth=4.5)

def test_never_underestimates_frequency():
    cms = CountMinSketch(width=1_000, depth=3)
    items_and_counts = [
            ("foo", 1),
            ("bar", 24),
            ("baz", 101),
    ]

    for item, count in items_and_counts:
        for _ in range(count):
            cms.add(item)

    for item, true_count in items_and_counts:
        est = cms.frequency(item)
        print(est, true_count)
        assert est >= true_count


def test_heavy_hitters_detection():
    """Test that CMS can identify heavy hitters (most frequent items)."""
    cms = CountMinSketch(width=1000, depth=4)
    
    # create a distribution with clear heavy hitters
    heavy_hitters = [("popular1", 100), ("popular2", 80), ("popular3", 60)]
    regular_items = [(f"item_{i}", 1) for i in range(50)]
    
    all_items = heavy_hitters + regular_items
    
    for item, count in all_items:
        for _ in range(count):
            cms.add(item)
    
    # heavy hitters should have much higher estimated frequencies
    for item, true_count in heavy_hitters:
        estimated = cms.frequency(item)
        assert estimated >= true_count, f"Heavy hitter {item} underestimated"
        assert estimated >= 50, f"Heavy hitter {item} should have high frequency"
    
    # regular items should have low frequencies
    for item, true_count in regular_items[:10]:  # Sample check
        estimated = cms.frequency(item)
        assert estimated >= true_count, "Should never underestimate"
        assert estimated <= 20, f"Regular item {item} estimated too high: {estimated}"


def test_handle_counts_greater_than_255():
    """
    This test highlights that the current bytearray implementation
    caps counts at 255, which can lead to underestimation for
    very frequent items.
    """
    cms = CountMinSketch(width=1000, depth=4)
    item = "very_frequent_item"
    true_count = 300

    for _ in range(true_count):
        cms.add(item)

    estimated_freq = cms.frequency(item)

    # This assertion is expected to fail with the current implementation
    assert estimated_freq >= true_count


