from .lsm_tree import LSMTree

def test_put_and_get_single_item():
    lsm = LSMTree()
    key = "key"
    val = "val"
    lsm.put(key, val)
    assert lsm.get(key) == val
