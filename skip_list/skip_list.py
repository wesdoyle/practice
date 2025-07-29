import random
from typing import Optional


class SkipListNode:
    def __init__(self, key, level):
        self._key = key
        self._forward = [None] * (level + 1)


class SkipList:
    def __init__(self, max_level=16, probability=0.5):
        """
        Initialize skip list with configurable parameters.
        max_level: maximum number of levels (affects performance)
        probability: probability of promoting to next level
        """
        self.max_level = max_level
        self.probability = probability
        self.level = 0  # Current highest level in use

        # Create head node (sentinel) with maximum possible levels
        self.head = SkipListNode(None, max_level)

    def insert(self, key):
        """Insert a key into the skip list."""
        # Array to track update positions at each level
        update = [None] * (self.max_level + 1)
        current = self.head

        # Search down from top level to find insertion point
        for i in range(self.level, -1, -1):
            while current._forward[i] is not None and current._forward[i]._key < key:
                current = current._forward[i]
            update[i] = current

        # Move to next node (potential duplicate)
        current = current._forward[0]

        # If key doesn't exist, create new node
        if current is None or current._key != key:
            # Generate random level for new node
            new_level = self.generate_random_level()

            # If new level exceeds current level, update pointers
            if new_level > self.level:
                for i in range(self.level + 1, new_level + 1):
                    update[i] = self.head
                self.level = new_level

            # Create and link new node
            new_node = SkipListNode(key, new_level)
            for i in range(new_level + 1):
                new_node._forward[i] = update[i]._forward[i]
                update[i]._forward[i] = new_node

    def contains(self, key):
        """Check if a key exists in the skip list."""
        current = self.head

        # Search down from top level
        for i in range(self.level, -1, -1):
            while current._forward[i] is not None and current._forward[i]._key < key:
                current = current._forward[i]

        # Check if we found the key
        current = current._forward[0]
        return current is not None and current._key == key

    def delete(self, key):
        """Delete a key from the skip list."""
        # Array to track update positions
        update = [None] * (self.max_level + 1)
        current = self.head

        # Search for deletion point
        for i in range(self.level, -1, -1):
            while current._forward[i] is not None and current._forward[i]._key < key:
                current = current._forward[i]
            update[i] = current

        current = current._forward[0]

        # If key exists, delete it
        if current is not None and current._key == key:
            # Update forward pointers
            for i in range(self.level + 1):
                if update[i]._forward[i] != current:
                    break
                update[i]._forward[i] = current._forward[i]

            # Update level if necessary
            while self.level > 0 and self.head._forward[self.level] is None:
                self.level -= 1

            return True
        return False

    def generate_random_level(self):
        """Generate a random level for a node using geometric distribution."""
        level = 0
        while random.random() < self.probability and level < self.max_level:
            level += 1
        return level

    def get_structure_info(self):
        """Return information about the internal structure for testing purposes."""
        # Count nodes by traversing level 0
        node_count = 0
        current = self.head._forward[0]
        while current is not None:
            node_count += 1
            current = current._forward[0]

        return {
            "max_level": self.max_level,
            "probability": self.probability,
            "current_height": self.level,  # Now returns actual height
            "node_count": node_count,
        }

    def to_list(self):
        """Return all items in sorted order."""
        result = []
        current = self.head._forward[0]  # Start from first real node

        while current is not None:
            result.append(current._key)
            current = current._forward[0]

        return result
