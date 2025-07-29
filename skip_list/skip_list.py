class SkipList:
    def __init__(self):
        self._items = set()

    def contains(self, key: str | int | float):
        return key in self._items

    def insert(self, key: str | int | float):
        self._items.add(key)
