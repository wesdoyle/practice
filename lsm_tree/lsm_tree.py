from typing import Optional


class LSMTree:
    TOMBSTONE = "<deleted>"

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
            value = self._memtable[key]
            return None if value == self.TOMBSTONE else value

        for sstable in reversed(self.sstables):
            if key in sstable:
                value = sstable[key]
                return None if value == self.TOMBSTONE else value

        return None

    def delete(self, key: str) -> None:
        self._memtable[key] = self.TOMBSTONE
        if len(self._memtable) >= self.memtable_size_limit:
            self._flush_memtable()

    def compact(self) -> None:
        if len(self.sstables) <= 1:
            return None

        merged_data: dict[str,str] = dict()

        # process oldest to newest so newer values override
        for sstable in self.sstables:
            for k, v in sstable.items():
                merged_data[k] = v

        compacted_data = {
                k: v
                for k, v in merged_data.items()
                if v != self.TOMBSTONE
        }

        self.sstables = [compacted_data] if compacted_data else []

    def _flush_memtable(self):
        if self._memtable:
            sorted_data = dict(sorted(self.memtable.items()))
            self.sstables.append(sorted_data)
            self._memtable.clear()

    @property
    def memtable(self):
        return self._memtable
