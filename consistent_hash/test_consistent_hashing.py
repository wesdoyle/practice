from .consistent_hashing import ConsistentHashRing


def test_single_node_always_selected():
    ring = ConsistentHashRing(nodes=["node1"], virtual_nodes=10, replication_factor=1)
    key = "test_key"
    assert ring.get_node(key) == "node1"


def test_empty_ring_behavior():
    ring = ConsistentHashRing(nodes=[], virtual_nodes=10, replication_factor=1)
    assert ring.get_node("any") is None
    assert ring.get_nodes_for_key("any") == []


def test_same_key_maps_to_same_node():
    ring = ConsistentHashRing(
        nodes=["node1", "node2", "node3"], virtual_nodes=50, replication_factor=1
    )
    key = "persistent-key"
    assert ring.get_node(key) == ring.get_node(key)
    assert ring.get_node(key) is not None


def test_none_key_is_no_op():
    ring = ConsistentHashRing(
        nodes=["node1", "node2", "node3"], virtual_nodes=50, replication_factor=1
    )
    key = None
    assert ring.get_node(key) is None


def test_keys_distribute_across_nodes():
    ring = ConsistentHashRing(
        nodes=["node1", "node2", "node3"], virtual_nodes=50, replication_factor=1
    )
    keys = ["foo", "bar", "baz", "qux"]
    assigned_nodes = {ring.get_node(k) for k in keys}
    assert len(assigned_nodes) > 1


def test_get_multiple_replicas_for_key():
    ring = ConsistentHashRing(
        nodes=["n1", "n2", "n3", "n4"], virtual_nodes=100, replication_factor=2
    )
    key = "resilient_key"
    replicas = ring.get_nodes_for_key(key)
    assert len(replicas) == 2
    assert len(set(replicas)) == 2


def test_removing_node_reassigns_keys():
    ring = ConsistentHashRing(
        nodes=["a", "b", "c"], virtual_nodes=100, replication_factor=2
    )
    key = "some_key"
    original_node = ring.get_node(key)
    ring.remove_node(original_node)
    new_node = ring.get_node(key)
    assert new_node != original_node
    assert new_node in {"a", "b", "c"} - {original_node}


def test_removing_none_node_is_no_op():
    ring = ConsistentHashRing(
        nodes=["a", "b", "c"], virtual_nodes=100, replication_factor=2
    )
    key = None
    original_node = ring.get_node(key)
    ring.remove_node(original_node)
    new_node = ring.get_node(key)
    assert new_node is None
    assert new_node not in {"a", "b", "c"}


def test_all_nodes_receive_some_keys():
    ring = ConsistentHashRing(
        nodes=["a", "b", "c"], virtual_nodes=100, replication_factor=1
    )
    keyspace = [f"key{i}" for i in range(100)]
    node_counts = {node: 0 for node in ring.nodes}
    for key in keyspace:
        node = ring.get_node(key)
        node_counts[node] += 1

    for node in ring.nodes:
        assert node_counts[node] > 0, f"{node} received no keys"
