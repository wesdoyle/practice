class SkipList:
    def __init__(self):
        self._items = set()

    def contains(self, key: str | int | float) -> bool:
        return key in self._items

    def insert(self, key: str | int | float) -> None:
        self._items.add(key)
        return None

    def to_list(self) -> list:
        return sorted(list(self._items))
