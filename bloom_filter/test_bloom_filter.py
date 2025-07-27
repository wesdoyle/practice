from .bloom_filter import BloomFilter

def test_empty_filter_contains_nothing():
    bf = BloomFilter()
    assert not bf.contains("foo")
    assert not bf.contains("")

def test_contains_gets_added_item():
    bf = BloomFilter()
    bf.add("foo")
    assert bf.contains("foo")
