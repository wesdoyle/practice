import hashlib
import bisect
from typing import Optional


class ConsistentHashRing:
    """
    Consistent hash ring implementation with virtual nodes and fault-tolerant key replication

    This class maps keys to 'physical nodes' in a way that minimized disruptions when nodes are added or removed.
    Each physical node can be represented multiple time in the hash ring via virtual nodes, and keys can be
    replicated to multiple distinct nodes for redundancy.

    Attributes:
        virtual_nodes (int): Number of virtual hash points per physical nodes
        replication_factor (int): Number of distinct physical nodes each key is assigned to
    """

    def __init__(
        self,
        nodes: Optional[list] = None,
        virtual_nodes: int = 100,
        replication_factor: int = 1,
    ) -> None:
        """
        Initialize the hash ring

        Args:
            nodes (Iterable[str], optional): Initial list of node identifiers
            virtual_nodes (int): Number of virtual nodes per physical node to smooth distribution
            replication_factor (int): Number of distinct nodes to replicate each key to
        """
        self.virtual_nodes = virtual_nodes
        self.ring = dict()
        self.sorted_keys = []
        self.nodes = set()
        self.replication_factor = replication_factor

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        """Return an integer hash of the given string using SHA-256"""
        return int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        """
        Add a 'physical node' to the hash ring

        Args:
            node (str): Identifier for the node
        """
        self.nodes.add(node)
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            h = self._hash(virtual_key)
            self.ring[h] = node
            bisect.insort(self.sorted_keys, h)
        return None

    def get_node(self, key: str | None) -> str | None:
        """
        Get the primary node responsible for a given key

        Args:
            node (str|None): the key to assign

        Returns:
            str|None: the node responsible, or None if the ring is empty
        """
        if not self.ring:
            return None
        if not key:
            return None
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h)
        if idx == len(self.sorted_keys):
            idx = 0  # wrap around
        return self.ring[self.sorted_keys[idx]]

    def get_nodes_for_key(self, key: str) -> list[str]:
        """
        Get a list of distinct nodes responsible for storing the given key

        Args:
            key (str): The key to replicate

        Returns:
            List[str]: a list of up to 'replication_factor' distinct nodes
        """
        if not self.ring or self.replication_factor == 0:
            return []
        h = self._hash(key)
        start_idx = bisect.bisect(self.sorted_keys, h)
        found = set()
        replicas = []
        idx = start_idx
        while len(replicas) < self.replication_factor and len(found) < len(self.nodes):
            ring_idx = idx % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[ring_idx]]
            if node not in found:
                found.add(node)
                replicas.append(node)
            idx += 1
        return replicas

    def remove_node(self, node: str | None) -> None:
        """
        Remove a 'physical node' and all its virtual representations from the hash ring

        Args:
            node (str): Identifier of the node to remove
        """
        if node is None:
            return None
        self.nodes.discard(node)
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            h = self._hash(virtual_key)
            if h in self.ring:
                del self.ring[h]
                idx = bisect.bisect_left(self.sorted_keys, h)
                if idx < len(self.sorted_keys) and self.sorted_keys[idx] == h:
                    self.sorted_keys.pop(idx)
        return None
