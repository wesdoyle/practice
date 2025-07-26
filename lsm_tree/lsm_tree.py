from typing import Optional


class LSMTree:
    def __init__(self, memtable_size_limit=10):
        self.memtable_size_limit = memtable_size_limit
        self._memtable: dict[str,str] = dict()
        self.sstables: list[dict[str,str]] = []

    def put(self, key: str, val: str):
        self._memtable[key] = val
        if len(self._memtable) >= self.memtable_size_limit:
            self._flush_memtable()

    def get(self, key: str) -> Optional[str]:
        if key in self._memtable:
            return self._memtable[key]

        for sstable in reversed(self.sstables):
            if key in sstable:
                return sstable[key]
        return None

    def _flush_memtable(self):
        if self._memtable:
            sorted_data = dict(sorted(self.memtable.items()))
            self.sstables.append(sorted_data)
            self._memtable.clear()

    @property
    def memtable(self):
        return self._memtable
