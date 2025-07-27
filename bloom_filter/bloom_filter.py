class BloomFilter:

    def __init__(self, expected_items: int = 1_000, false_pos_rate=0.01):
        self._expeted_items = expected_items
        self._false_pos_rate = false_pos_rate
        self._items = set()

    def contains(self, key: str):
        return key in self._items

    def add(self, key: str):
        self._items.add(key)
