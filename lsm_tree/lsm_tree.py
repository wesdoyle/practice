from typing import Optional, NamedTuple


class Entry(NamedTuple):
    key: str
    value: str
    sequence: int


class LSMTree:
    TOMBSTONE = "<deleted>"

    def __init__(self, memtable_size_limit=10):
        self.memtable_size_limit = memtable_size_limit
        self._memtable: dict[str, Entry] = dict()
        self.sstables: list[list[Entry]] = []
        self.next_seq = 1

    def put(self, key: str, val: str) -> None:
        entry = Entry(key, val, self.next_seq)
        self._memtable[key] = entry
        self.next_seq += 1

        if len(self._memtable) >= self.memtable_size_limit:
            self._flush_memtable()

        return None

    def get(self, key: str) -> Optional[str]:
        if key in self._memtable:
            entry = self._memtable[key]

            return None if entry.value == self.TOMBSTONE else entry.value

        for sstable in reversed(self.sstables):
            latest_entry = None

            for entry in reversed(sstable):
                if entry.key == key:
                    latest_entry = entry
                    break

            if latest_entry:
                return (
                    None if latest_entry.value == self.TOMBSTONE else latest_entry.value
                )

        return None

    def delete(self, key: str) -> None:
        entry = Entry(key, self.TOMBSTONE, self.next_seq)
        self._memtable[key] = entry
        self.next_seq += 1

        if len(self._memtable) >= self.memtable_size_limit:
            self._flush_memtable()

    def compact(self) -> None:
        if len(self.sstables) <= 1:
            return None

        all_entries: list[Entry] = []

        for sstable in self.sstables:
            all_entries.extend(sstable)

        all_entries.sort(key=lambda x: x.sequence)

        latest_entries: dict[str, Entry] = dict()
        for entry in all_entries:
            latest_entries[entry.key] = entry

        # remove tombstones
        compacted_entries = [
            entry for entry in latest_entries.values() if entry.value != self.TOMBSTONE
        ]

        # sort by sequence
        compacted_entries.sort(key=lambda x: x.sequence)

        # replace sstables with the compacted copy
        self.sstables = [compacted_entries] if compacted_entries else []

    def scan(self, start_key: str, end_key: str) -> list[tuple[str, str]]:
        """scans a range of keys, returning sorted k-v pairs"""
        results: list[Entry] = []

        # collect data from sstables (oldest first, newest overrides)
        for sstable in self.sstables:
            for entry in sstable:
                if start_key <= entry.key <= end_key:
                    results.append(entry)

        # overwrite with current memtable data
        for entry in self._memtable.values():
            if start_key <= entry.key <= end_key:
                results.append(entry)

        results.sort(key=lambda x: x.sequence)

        latest_entries: dict[str, Entry] = dict()

        for entry in results:
            latest_entries[entry.key] = entry

        sorted_results = [
            (entry.key, entry.value)
            for entry in sorted(latest_entries.values(), key=lambda e: e.key)
            if entry.value != self.TOMBSTONE
        ]

        return sorted_results

    def _flush_memtable(self):
        if self._memtable:
            entries = list(self.memtable.values())
            entries.sort(key=lambda x: x.sequence)
            self.sstables.append(entries)
            self._memtable.clear()

    @property
    def memtable(self):
        return self._memtable
