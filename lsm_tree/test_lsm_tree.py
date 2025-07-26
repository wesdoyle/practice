from .lsm_tree import LSMTree

def test_put_and_get_single_item():
    lsm = LSMTree()
    key = "key"
    val = "val"
    lsm.put(key, val)
    assert lsm.get(key) == val

def test_get_nonexistent_key_returns_none():
    lsm = LSMTree()
    key = "foo"
    assert lsm.get(key) is None

def test_update_existing_key_overwrites_old_value():
    lsm = LSMTree()
    key = "foo"
    lsm.put(key, "hello")
    lsm.put(key, "world")
    val = lsm.get(key)
    assert val == "world"

