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

def test_maintains_sorted_order_of_keys():
    sl = SkipList()
    items = [0,9,3,7,2]
    for item in items:
        sl.insert(item)
    sorted_items = sl.to_list()
    expected = [0,2,3,7,9]
    assert sorted_items == expected


