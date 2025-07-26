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


def test_compact_removes_tombstones():
    lsm = LSMTree(memtable_size_limit=1)
    lsm.put("key1", "v1")  # flush
    lsm.delete("key1")     # flush
    lsm.put("key2", "v2")  # flush

    assert len(lsm.sstables) == 3

    lsm.compact()

    assert len(lsm.sstables) == 1
    assert lsm.get("key1") is None
    assert lsm.get("key2") == "v2" 


def test_can_scan_range():
    lsm = LSMTree()
    lsm.put("k1", "v1")
    lsm.put("k2", "v2")
    lsm.put("k3", "v3")
    lsm.put("k4", "v4")

    results = lsm.scan("k2", "k4")
    expected = [("k2", "v2"), ("k3", "v3"), ("k4", "v4")]
    assert results == expected

def test_scan_range_with_sstables_and_deletions():
    lsm = LSMTree(memtable_size_limit=2)
    lsm.put("a", "1")
    lsm.put("b", "2")  # flush
    lsm.put("b", "updated")
    lsm.put("c", "3")  # flush
    lsm.delete("a")

    results = lsm.scan("a", "z")
    expected = [("b", "updated"), ("c", "3")]
    assert results == expected

def test_end_to_end_workflow():
    lsm = LSMTree(memtable_size_limit=3)
    test_data = [("user_1", "alice"), ("user_2", "bob"), ("user_3", "angel")]
    for k, v in test_data:
        lsm.put(k, v)

    lsm.put("user_1", "alice_v2")
    lsm.put("user_4", "david")
    lsm.put("user_5", "eve")

    assert len(lsm.sstables) == 2  # at this point we should have two sstables
    assert lsm.get("user_1") == "alice_v2"
    assert lsm.get("user_5") == "eve"

    lsm.delete("user_2")
    lsm.put("user_6", "otto")

    lsm.compact()
    assert len(lsm.sstables) == 1

    expected = [("user_1", "alice_v2"), ("user_3", "angel"), ("user_4", "david"), ("user_5", "eve"), ("user_6", "otto")]

    for k, v in expected:
        assert lsm.get(k) == v

    assert lsm.get("user_2") is None

    scan_results = lsm.scan("user_1", "user_6")
    assert len(scan_results) == 5


