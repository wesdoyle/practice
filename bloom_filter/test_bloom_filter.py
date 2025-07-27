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
    items = [f"item:{i}" for i in range(1_000_000)]

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
    assert hasattr(bf, "bit_words")
    assert bf.contains("foo")
