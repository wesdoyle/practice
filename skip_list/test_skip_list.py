from .skip_list import SkipList
import time
import random


def test_can_create_skip_list():
    sl = SkipList()
    assert sl is not None


def test_empty_skip_list_contains_nothing():
    sl = SkipList()
    assert not sl.contains("foo")
    assert not sl.contains(123)
    assert not sl.contains(0)


def test_can_insert_and_find_items():
    sl = SkipList()
    sl.insert("foo")
    assert sl.contains("foo")


def test_maintains_sorted_order_of_keys():
    sl = SkipList()
    items = [0, 9, 3, 7, 2]
    for item in items:
        sl.insert(item)
    sorted_items = sl.to_list()
    expected = [0, 2, 3, 7, 9]
    assert sorted_items == expected


def test_performance_scales_better_than_linear_search():
    """Test that search performance scales better than O(n) - behavioral test for skip list structure."""

    sl = SkipList()

    n_small = 1_000
    n_large = 10_000

    for i in range(n_small):
        sl.insert(i)

    start_time = time.time()
    for _ in range(100):
        sl.contains(n_small // 2)  # Search for middle element
    small_time = time.time() - start_time

    for i in range(n_small, n_large):
        sl.insert(i)

    start_time = time.time()
    for _ in range(100):
        sl.contains(n_large // 2)  # Search for middle element
    large_time = time.time() - start_time

    time_ratio = large_time / small_time if small_time > 0 else 1

    assert time_ratio < 10, f"Performance degraded too much: {time_ratio}x slower"


def test_can_configure_probabilistic_parameters():
    """Test that skip list accepts configuration parameters"""
    sl_default = SkipList()
    sl_custom = SkipList(max_level=8, probability=0.25)

    sl_default.insert(42)
    sl_custom.insert(42)

    assert sl_default.contains(42)
    assert sl_custom.contains(42)

    data = list(range(100))
    for item in data:
        sl_default.insert(item)
        sl_custom.insert(item)

    assert sl_default.to_list() == data
    assert sl_custom.to_list() == data


def test_can_delete_items_maintaining_sorted_order():
    """Test deletion functionality - drives toward proper skip list implementation."""
    sl = SkipList()

    items = [5, 2, 8, 1, 9, 3, 7, 4, 6]
    for item in items:
        sl.insert(item)
    assert sl.to_list() == sorted(items)

    # delete some items
    deleted = sl.delete(5)
    assert deleted is True

    # verify item is gone
    assert not sl.contains(5)
    assert sl.to_list() == [1, 2, 3, 4, 6, 7, 8, 9]

    # delete non-existent item
    deleted = sl.delete(99)
    assert not deleted

    # List should be unchanged
    assert sl.to_list() == [1, 2, 3, 4, 6, 7, 8, 9]

    # delete from ends
    sl.delete(1)  # delete first
    sl.delete(9)  # delete last

    assert sl.to_list() == [2, 3, 4, 6, 7, 8]


def test_handles_large_range_with_sparse_data_efficiently():
    """Test efficiency with sparse data"""
    sl = SkipList()

    # insert very sparse data (would be inefficient with range-based storage)
    sparse_data = [1, 1_000_000_000, 2_000_000_000, 3_000_000_000]

    for value in sparse_data:
        sl.insert(value)

    # Should handle this efficiently
    assert sl.to_list() == sparse_data

    # Should be able to search efficiently
    assert sl.contains(1_000_000_000)
    assert not sl.contains(500_000_000)

    # Should be able to delete efficiently
    sl.delete(2_000_000_000)
    assert sl.to_list() == [1, 1_000_000_000, 3_000_000_000]

    # Insert something in the middle
    sl.insert(1_500_000_000)
    assert sl.to_list() == [1, 1_000_000_000, 1_500_000_000, 3_000_000_000]


def test_demonstrates_logarithmic_height_property():
    """Test that structure height grows logarithmically - behavioral test for skip list."""

    datasets = [100, 1_000, 10_000]
    measurements = []

    for n in datasets:
        # create fresh skip list for each measurement
        test_sl = SkipList(max_level=20, probability=0.5)

        for i in range(n):
            test_sl.insert(i)

        search_count = min(100, n // 10)  # scale searches linearly wrt dataset size
        start_time = time.time()

        for i in range(search_count):
            test_sl.contains(i * (n // search_count))

        total_time = time.time() - start_time
        avg_time_per_search = total_time / search_count if search_count > 0 else 0

        measurements.append(avg_time_per_search)

    # Verify that performance doesn't degrade dramatically
    first_measurement = measurements[0]
    last_measurement = measurements[-1]

    if first_measurement > 0:
        performance_ratio = last_measurement / first_measurement
        # should not degrade by more than a reasonable factor
        assert (
            performance_ratio < 100
        ), f"Performance degraded too much: {performance_ratio}x"

    assert len(measurements) == len(datasets)
    assert all(m >= 0 for m in measurements)


def test_can_generate_random_levels_for_probabilistic_structure():
    """Test that we can generate random levels"""
    sl = SkipList(max_level=5, probability=0.5)

    levels = []
    for _ in range(1_000):
        level = sl.generate_random_level()
        levels.append(level)
        assert 0 <= level <= sl.max_level, f"Level {level} out of bounds"

    # should see a distribution where level 0 is most common
    level_counts = {}
    for level in levels:
        level_counts[level] = level_counts.get(level, 0) + 1

    # with prob 0.5, about 50% should be level 0, 25% level 1, etc.
    level_0_count = level_counts.get(0, 0)
    level_1_count = level_counts.get(1, 0)

    assert (
        level_0_count > level_1_count
    ), f"Level 0 ({level_0_count}) should be more frequent than level 1 ({level_1_count})"

    unique_levels = len(level_counts)
    assert (
        unique_levels >= 2
    ), f"Should see variety in levels, got {unique_levels} different levels"


def test_structure_height_increases_with_more_items():
    """Test that adding more items tends to increase the structure height."""
    random.seed(42)

    sl = SkipList(max_level=10, probability=0.5)

    initial_info = sl.get_structure_info()
    assert initial_info["current_height"] == 0

    previous_height = 0
    height_increased = False

    for i in range(100):
        sl.insert(i)

        current_info = sl.get_structure_info()
        current_height = current_info["current_height"]

        # height should never decrease (skip list property)
        assert current_height >= previous_height, "Height should never decrease"

        # track if we ever see height increase
        if current_height > previous_height:
            height_increased = True

        previous_height = current_height

    assert (
        height_increased
    ), "Height should increase as items are added to skip list structure"

    final_info = sl.get_structure_info()
    assert final_info["current_height"] > 0, "Final structure should have height > 0"
