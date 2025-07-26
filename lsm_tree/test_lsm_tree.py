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

def test_memtable_flush_when_full():
    lsm = LSMTree(memtable_size_limit=3)
    lsm.put("k1", "v1")
    assert len(lsm.memtable) == 1

    lsm.put("k2", "v2")
    assert len(lsm.memtable) == 2

    lsm.put("k3", "v3")
    assert len(lsm.memtable) == 0

    assert lsm.get("k1") == "v1"
    assert lsm.get("k2") == "v2"
    assert lsm.get("k3") == "v3"
