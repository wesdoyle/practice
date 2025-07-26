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

def test_delete_overrides_sstable_value():
    """Test that deletion tombstone overrides values in SSTables"""
    lsm = LSMTree(memtable_size_limit=1)
    lsm.put("key", "value1")  # flushes immediately
    assert lsm.get("key") == "value1"
    lsm.delete("key")
    assert lsm.get("key") is None


def test_sstables_are_length_1_after_compaction():
    """Test multiple SSTables compacted into one"""
    lsm = LSMTree(memtable_size_limit=2)
    lsm.put("a", "1")
    lsm.put("b", "2")
    lsm.put("a", "updated")
    lsm.put("c", "3")

    assert len(lsm.sstables) == 2
    lsm.compact()

    assert len(lsm.sstables) == 1

    assert lsm.get("a") == "updated"
    assert lsm.get("b") == "2"
    assert lsm.get("c") == "3"



    assert len(lsm.sstables) == 3

    lsm.compact()

    assert len(lsm.sstables) == 1
    assert lsm.get("key1") is None
    assert lsm.get("key2") == "v2" 

