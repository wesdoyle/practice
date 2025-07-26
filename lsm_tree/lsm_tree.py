from typing import Optional


class LSMTree:
    def __init__(self):
        self.memtable: dict[str,str] = dict()

    def put(self, key: str, val: str):
        self.memtable[key] = val

    def get(self, key: str) -> Optional[str]:
        return self.memtable.get(key)
