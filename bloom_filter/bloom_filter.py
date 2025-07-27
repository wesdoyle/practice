class BloomFilter:

    def __init__(self):
        self._items = set()

    def contains(self, key: str):
        return key in self._items

    def add(self, key: str):
        self._items.add(key)
