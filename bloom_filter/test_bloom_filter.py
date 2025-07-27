from .bloom_filter import BloomFilter

def test_empty_filter_contains_nothing():
    bf = BloomFilter()
    assert not bf.contains("foo")
    assert not bf.contains("")

def test_contains_gets_added_item():
    bf = BloomFilter()
    bf.add("foo")
    assert bf.contains("foo")
    assert not bf.contains("bar")

def test_no_false_negatives():
    bf = BloomFilter()
    items = [f"item:{i}" for i in range(100_000)]

    for item in items:
        bf.add(item)

    for item in items:
        assert bf.contains(item)

def test_can_create_with_expected_items_param():
    bf = BloomFilter(expected_items=1_000)
    assert bf is not None
    bf.add("x")
    assert bf.contains("x")

def test_can_create_with_false_positives_param():
    bf = BloomFilter(expected_items=256, false_pos_rate=0.001)
    assert bf is not None
    bf.add("x")
    assert bf.contains("x")

def test_uses_bit_array():
    bf = BloomFilter(expected_items=256, false_pos_rate=0.001)
    bf.add("foo")
    assert hasattr(bf, "_bit_words")
    assert bf.contains("foo")

def test_bitwise_ops_work_as_expected():
    bf = BloomFilter(expected_items=256)
    bf._set_bit(0)
    bf._set_bit(63)
    bf._set_bit(64)
    bf._set_bit(127)

    assert bf._get_bit(0) is True
    assert bf._get_bit(63) is True
    assert bf._get_bit(64) is True
    assert bf._get_bit(127) is True 

    assert bf._get_bit(1) is False
    assert bf._get_bit(2) is False
    assert bf._get_bit(-1) is False
    assert bf._get_bit(128) is False

def test_allows_some_false_positives():
    bf = BloomFilter(expected_items=1_000, false_pos_rate=0.01)
    added = set()
    for i in range(500):
        item = f"item:{i}"
        bf.add(item)
        added.add(item)

    false_pos = 0
    test_count = 1_000

    for i in range(test_count):
        test_item = f"not_added:{i}"
        if test_item not in added and bf.contains(test_item):
            false_pos += 1
    
    fp_rate = false_pos / test_count

    # Should have some false positives (proves it's not just storing everything)
    # But not too many (proves the rate control works)
    print(fp_rate)
    assert 0 < fp_rate < .1
