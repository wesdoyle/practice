from .skip_list import SkipList


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

