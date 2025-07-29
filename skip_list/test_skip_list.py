from .skip_list import SkipList


def test_can_create_skip_list():
    sl = SkipList()
    assert sl is not None
